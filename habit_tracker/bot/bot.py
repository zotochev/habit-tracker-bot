from aiogram import Bot, Dispatcher

import config

from .handlers import router
from . import state_machine  # state-machine initialization
from . import middlewares
import bot as bot_module


bot = Bot(token=config.BOT_TOKEN)
bot_module.bot_instance = bot
dp = Dispatcher()


async def run_bot():
    dp.include_router(router)

    for middleware in middlewares.m:
        dp.message.middleware(middleware)
        dp.callback_query.middleware(middleware)

    await dp.start_polling(bot)
