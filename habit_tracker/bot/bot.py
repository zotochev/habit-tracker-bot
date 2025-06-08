from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

from .handlers.start import router


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def run_bot():
    dp.include_router(router)
    await dp.start_polling(bot)
