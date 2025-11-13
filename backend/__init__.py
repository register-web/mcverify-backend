from __future__ import annotations

from fastapi import FastAPI

from backend import routes


def create_app() -> FastAPI:
    app = FastAPI(title="MC Verify API")
    app.include_router(routes.router)
    return app
