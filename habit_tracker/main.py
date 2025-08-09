import asyncio
import logging

from bot.bot import run_bot
from bot.notificator import setup_notificator
from bot.utils import is_bot_ready_to_start
from web.http_server import run_http

from core.localizator.load_locales import setup_localizator
from bot.cache import setup_cache
from bot.messenger_queue import setup_messenger_queue
from config import LOCALES_DIRECTORY


logger = logging.getLogger(__name__)


async def main():
    if not (await is_bot_ready_to_start()):
        logger.error("Bot is not ready to start exiting.")
        return

    setup_localizator(LOCALES_DIRECTORY)
    messenger_queue = setup_messenger_queue()
    setup_cache(messenger_queue)
    notificator = setup_notificator(messenger_queue)

    await asyncio.gather(
        run_http(),
        run_bot(),
        messenger_queue.process_messages(),
        notificator.process_notifications(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting from app")
