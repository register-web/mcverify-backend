from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router as api_router
from migrate import run as run_migrations


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(title="Minecraft Verification API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.on_event("startup")
    async def apply_migrations() -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_migrations)

    @app.get("/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app
