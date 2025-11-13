from __future__ import annotations

import asyncio
import logging

import uvicorn

from backend import create_app
from bot import create_bot, create_dispatcher

logging.basicConfig(level=logging.INFO)

app = create_app()


async def start_fastapi() -> None:
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def start_bot() -> None:
    bot = create_bot()
    dispatcher = create_dispatcher()
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


async def main() -> None:
    await asyncio.gather(start_fastapi(), start_bot())


if __name__ == "__main__":
    asyncio.run(main())
