from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer("👋 Hello! Use /log to test backend.")


@router.message()
async def echo(message: Message):
    await message.answer(f"You said: {message.text}")


async def run_bot():
    dp.include_router(router)
    await dp.start_polling(bot)
