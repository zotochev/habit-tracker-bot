from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.cache import UserCache


router = Router()


@router.message(Command('start'))
async def start_handler(message: Message, user_cache: UserCache):
    await user_cache.state_machine.handle(message)
