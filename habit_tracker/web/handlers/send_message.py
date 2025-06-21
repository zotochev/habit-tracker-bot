from fastapi import Header
from fastapi import APIRouter

from bot import bot_instance
from data.schemas.send_message import SendMessageRequest


router = APIRouter()


@router.post("/send-message/")
async def send_message(req: SendMessageRequest, x_secret: str = Header(None)):
    await bot_instance.send_message(req.user_id, req.message)
