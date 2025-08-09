import logging
from asyncio.exceptions import CancelledError

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.types.input_file import InputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import config
from core.bot_mode import BotMode

from .handlers import router
from . import state_machine  # state-machine initialization
from . import middlewares
import bot as bot_module


logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
bot_module.bot_instance = bot
dp = Dispatcher()


async def run_polling(dp: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook()
    await dp.start_polling(bot)


async def run_webhook(dp: Dispatcher, bot: Bot) -> None:
    async def on_startup(bot: Bot) -> None:
        certificate = None
        if config.WEBHOOK_CERTIFICATE_PATH:
            # If you have a self-signed SSL certificate, then you will need to send a public
            # certificate to Telegram
            certificate = InputFile(config.WEBHOOK_CERTIFICATE_PATH)

        await bot.set_webhook(
            f"{config.WEBHOOK_HOST}{config.WEBHOOK_PATH}",
            certificate=certificate,
            secret_token=config.WEBHOOK_SECRET,
        )

    dp.startup.register(on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    await web._run_app(app, host=config.WEB_SERVER_HOST, port=config.WEB_SERVER_PORT)


async def run_bot():
    dp.include_router(router)

    for middleware in middlewares.m:
        dp.message.middleware(middleware)
        dp.callback_query.middleware(middleware)

    try:
        match config.BOT_MODE:
            case BotMode.polling:
                logger.info("Starting Bot in polling mode.")
                await run_polling(dp, bot)
            case BotMode.webhook:
                logger.info("Starting Bot in webhook mode.")
                await run_webhook(dp, bot)
            case _:
                raise AssertionError(f"Unexpected bot mode: {config.BOT_MODE}")
    except (KeyboardInterrupt, CancelledError) as e:
        logging.info(f"Exiting from bot: {e.__class__.__name__}:{e}")
