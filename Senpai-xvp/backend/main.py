from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import agent_control, task_input, logs, firebase_integration
from backend.services import planner, observer, executor, recorder, vm_manager, ai_assistance
import logging
import os
import sys
from backend import database  # Import the database module
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from typing import Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Senpai-xvp AI Agent System",
    description="A modular AI agent for natural language browser automation.",
    version="0.1.0",
    docs_url="/docs",  # Enable Swagger UI
    redoc_url="/redoc", # Enable ReDoc
)

#CORS middleware to allow cross-origin requests (for the UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (INSECURE FOR PRODUCTION)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_control.router, prefix="/agent", tags=["agent"])
app.include_router(task_input.router, prefix="/task", tags=["task"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
app.include_router(firebase_integration.router, prefix="/firebase", tags=["firebase"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: object, exc: StarletteHTTPException) -> JSONResponse:
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

def configure_services() -> None:
    """Initializes the application services."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.critical("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

    planner.Planner.initialize(openai_api_key)
    observer.Observer.initialize()
    executor.Executor.initialize()
    recorder.Recorder.initialize()
    vm_manager.VMManager.initialize()
    ai_assistance.AIAssistance.initialize(openai_api_key)
    logger.info("Application services initialized successfully.")

@app.on_event("startup")
async def startup_event() -> None:
    """Runs on application startup."""
    try:
        database.Base.metadata.create_all(bind=database.engine) # Create database tables
        configure_services()

    except ValueError as e:
        logger.critical(f"Startup failed due to configuration error: {e}")
        sys.exit(1) # Exit if a critical configuration is missing
    except Exception as e:
        logger.exception("Application startup failed due to an unexpected error.")
        sys.exit(1)  # Exit the application.

@app.get("/")
async def read_root() -> Dict[str, str]:
    """
    Returns a simple greeting.
    """
    return {"Hello": "World"}
