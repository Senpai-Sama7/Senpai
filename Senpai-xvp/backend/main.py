from fastapi import FastAPI
from backend.routes import agent_control, task_input, logs

app = FastAPI()

app.include_router(agent_control.router, prefix="/agent", tags=["agent"])
app.include_router(task_input.router, prefix="/task", tags=["task"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
