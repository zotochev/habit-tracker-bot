from fastapi import Header
from fastapi import APIRouter

from bot.bot import bot
from data.model.send_message import SendMessageRequest


router = APIRouter()


@router.post("/send-message/")
async def send_message(req: SendMessageRequest, x_secret: str = Header(None)):
    await bot.send_message(req.user_id, req.message)
