from fastapi import APIRouter

from src.core.rabbit_connection import rabbit_connection

router = APIRouter(prefix="/test", tags=["Test routes"])


@router.get("/")
async def process():
    message = {"type": "test_message", "message": "Test message text"}
    await rabbit_connection.send_messages(messages=message)
