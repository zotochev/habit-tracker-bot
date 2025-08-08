import asyncio

from bot.bot import run_bot
from web.http_server import run_http

from core.localizator.load_locales import setup_localizator
from bot.cache import setup_cache
from bot.messenger_queue import setup_messenger_queue
from config import LOCALES_DIRECTORY


async def main():
    setup_localizator(LOCALES_DIRECTORY)
    messenger_queue = setup_messenger_queue()
    setup_cache(messenger_queue)

    await asyncio.gather(
        run_http(),
        run_bot(),
        messenger_queue.process_messages(),
    )


if __name__ == "__main__":
    asyncio.run(main())
