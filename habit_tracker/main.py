import asyncio

from bot.bot import run_bot
from web.http_server import run_http

from core.localizator.load_locales import setup_localizator
from config import LOCALES_DIRECTORY


async def main():
    setup_localizator(LOCALES_DIRECTORY)

    await asyncio.gather(
        run_http(),
        run_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
