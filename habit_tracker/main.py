import asyncio

from bot.bot import run_bot
from web.http_server import run_http

from core.localizator.load_locales import setup_localizator
from bot.cache import setup_cache
from bot.messanger_queue import setup_messanger_queue
from config import LOCALES_DIRECTORY


async def main():
    setup_localizator(LOCALES_DIRECTORY)
    messanger_queue = setup_messanger_queue()
    setup_cache(messanger_queue)

    await asyncio.gather(
        run_http(),
        run_bot(),
        messanger_queue.process_messages(),
    )


if __name__ == "__main__":
    asyncio.run(main())
