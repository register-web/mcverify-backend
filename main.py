from __future__ import annotations

import asyncio
import logging
import os
import uvicorn

from backend.create_app import create_app
from bot import create_bot, create_dispatcher

logging.basicConfig(level=logging.INFO)

# 🌟 FastAPI приложение
app = create_app()


# 🚀 Запуск телеграм-бота
async def start_bot() -> None:
    bot = create_bot()
    dispatcher = create_dispatcher()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


# 🌟 Запускаем бота в фоне при старте FastAPI
@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(start_bot())


# 🚀 Запуск uvicorn, если файл запускают напрямую
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
