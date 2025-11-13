from __future__ import annotations

import asyncio
import logging

from backend.create_app import create_app
from bot import create_bot, create_dispatcher

logging.basicConfig(level=logging.INFO)

# 🌟 FastAPI приложение — именно это ищет uvicorn
app = create_app()


# 🚀 Функция запуска телеграм-бота
async def start_bot() -> None:
    bot = create_bot()
    dispatcher = create_dispatcher()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


# 🌟 Фоновая задача — запускается при старте FastAPI
@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(start_bot())
