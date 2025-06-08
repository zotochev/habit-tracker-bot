import asyncio

from bot.bot import run_bot
from web.http_server import run_http


async def main():
    await asyncio.gather(
        run_http(),
        run_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
