from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router as api_router
# from migrate import run as run_migrations   # ❌ отключено


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    
    app = FastAPI(
        title="Minecraft Verification API",
        version="1.0.0"
    )

    # CORS (можно потом ограничить только миниаппом)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем API роуты
    app.include_router(api_router)

    # ❌ Отключено, чтобы Railway не падал бесконечно
    #
    # @app.on_event("startup")
    # async def apply_migrations() -> None:
    #     loop = asyncio.get_running_loop()
    #     await loop.run_in_executor(None, run_migrations)

    # Healthcheck (Railway проверяет именно его)
    @app.get("/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app
