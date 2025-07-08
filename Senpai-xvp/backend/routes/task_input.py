from fastapi import APIRouter

router = APIRouter()

@router.post("/submit")
async def submit_task(task: str):
    return {"message": f"Task submitted: {task}"}