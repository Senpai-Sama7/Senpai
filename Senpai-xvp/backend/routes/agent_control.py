from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
async def start_agent():
    return {"message": "Agent started"}