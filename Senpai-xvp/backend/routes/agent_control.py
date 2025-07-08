from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from backend.services import ai_assistance, planner, executor, vm_manager, observer
from pydantic import BaseModel, validator
import asyncio
from sqlalchemy.orm import Session
from backend import database
from backend.database import AgentSession, LogEntry
import datetime
from sqlalchemy.orm.attributes import flag_modified
from typing import Coroutine

router = APIRouter()
logger = logging.getLogger(__name__)

class Task(BaseModel):
    description: str
    context: Dict[str, Any] = {}  # Optional context
    priority: int = 1  # Optional priority level
    template_name: str = "default_template.json" # Optional task template

    @validator("description")
    def description_must_not_be_empty(cls: object, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Description must not be empty or contain only whitespace")
        return v


async def execute_task(
    session_id: str,
    refined_task: str,
    db: Session,
    template_name: str = "default_template.json",
) -> None:
    """Executes the task, either by generating a plan or using a task template."""
    browser_session = None  # Initialize browser_session
    try:
        # 1. Get a browser session from the Executor
        browser_session = await executor.Executor.get_browser_session()
        if not browser_session:
            raise Exception("Failed to get browser session")

        # 2. Initial Context
        context = ""

        # Use task template if specified, otherwise, generate a plan
        plan: List[str] = []
        if template_name != "default_template.json":
            logger.info(f"Executing task using template: {template_name}")
            # Load actions from the template
            actions = recorder.Recorder.load_task_template(template_name)
            if not actions:
                raise Exception(f"Task template not found: {template_name}")
            # No plan is generated as it will use the task template
        else:
            # 3. Generate a plan from the Planner
            plan = planner.Planner.generate_plan(refined_task, context)
            logger.info(f"Generated plan: {plan}")

        # Log the plan
        log_message = f"Starting task: {refined_task} with plan: {plan if template_name == 'default_template.json' else template_name}"
        log_entry = LogEntry(session_id=session_id, message=log_message, level = 'INFO')
        db.add(log_entry)
        db.commit()

        # Update the database
        db_agent_session = db.query(AgentSession).filter(AgentSession.session_id == session_id).first()
        if not db_agent_session:
            raise Exception(f"Agent Session not found: {session_id}")

        db_agent_session.current_step = 0
        db.commit()
        db.refresh(db_agent_session)
        # 4. Execute the plan step-by-step
        if template_name == "default_template.json":
            for i, step in enumerate(plan):
                logger.info(f"Executing step {i+1}: {step}")
                log_message = f"Executing step {i+1}: {step}"
                log_entry = LogEntry(session_id=session_id, message=log_message, level = 'INFO')
                db.add(log_entry)
                db.commit()

                try:
                    # Capture DOM and screenshot before each step
                    observation = await observer.Observer.observe(browser_session)
                    dom = observation["dom"]
                    screenshot = observation["screenshot"]

                    # Pass the DOM and screenshot to execute_step
                    log_data = await executor.Executor.execute_step(browser_session, step, dom, screenshot)

                    #Update the database after each step
                    db_agent_session = db.query(AgentSession).filter(AgentSession.session_id == session_id).first()
                    if not db_agent_session:
                        raise Exception(f"Agent Session not found: {session_id}")

                    db_agent_session.current_step = i + 1
                    db_agent_session.last_action = log_data.get('action')
                    db_agent_session.last_dom = dom
                    db_agent_session.last_screenshot = screenshot
                    db.commit()
                    db.refresh(db_agent_session)

                except Exception as e:
                    logger.exception(f"Error executing step {i+1}: {step}")
                    log_message = f"Error executing step {i+1}: {step}: {e}"
                    log_entry = LogEntry(session_id=session_id, message=log_message, level = 'ERROR')
                    db.add(log_entry)
                    db.commit()
                    raise # Re-raise the exception to stop further execution
        else:
             # Execute all actions from the template
            logger.info(f"Executing all actions from the  template")
            # Capture DOM and screenshot before the template
            observation = await observer.Observer.observe(browser_session)
            dom = observation["dom"]
            screenshot = observation["screenshot"]
            await executor.Executor.execute_task_template(browser_session, template_name, dom, screenshot)

        # Task completed successfully
        log_message = "Task completed successfully."
        log_entry = LogEntry(session_id=session_id, message=log_message, level = 'INFO')
        db.add(log_entry)
        db.commit()
        db_agent_session.is_running = False  # update session status
        db_agent_session.end_time = datetime.datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.exception(f"Error executing task in session {session_id}")
        log_message = f"Error executing task: {e}"
        log_entry = LogEntry(session_id=session_id, message=log_message, level = 'ERROR')
        db.add(log_entry)
        db.commit()
        db_agent_session = db.query(AgentSession).filter(AgentSession.session_id == session_id).first()
        if db_agent_session:
           db_agent_session.is_running = False  # update session status
           db_agent_session.end_time = datetime.datetime.utcnow()
           db.commit()
    finally:
        # 4. Clean up resources and close browser if needed
        if browser_session:
            try:
                browser_session.quit()
            except Exception as e:
                logger.warning(f"Error closing browser session: {e}")


@router.post("/start")
async def start_agent(task: Task = Depends(), db: Session = Depends(database.get_db)) -> Dict[str, str]:
    """Starts an agent to execute a given task."""
    try:
        refined_task = await ai_assistance.AIAssistance.refine_task(task.description)
        logger.info(f"Refined task: {refined_task}")

        # Create a new VM session
        session_id = await vm_manager.VMManager.create_session()
        logger.info(f"Created new VM session with ID: {session_id}")

        # Create a new AgentSession in the database
        db_agent_session = AgentSession(
            session_id=session_id,
            task_description=task.description
        )
        db.add(db_agent_session)
        db.commit()
        db.refresh(db_agent_session)

        # Start the task execution in the background
        asyncio.create_task(execute_task(session_id, refined_task, db, task.template_name))

        return {"message": f"Agent started for task: {refined_task} in session {session_id}"}

    except Exception as e:
        logger.exception("Error starting agent")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
