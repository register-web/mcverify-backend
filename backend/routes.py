from __future__ import annotations

from fastapi import Depends, HTTPException, Query
from fastapi.routing import APIRouter
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.schemas import (
    ChangeNameRequest,
    PasswordRequest,
    PlayerResponse,
    RegisterRequest,
    StatusResponse,
)
from db import models
from utils.config import get_settings
from utils.security import needs_reverification, sha256_hex, utcnow, verify_telegram_hash

router = APIRouter()
settings = get_settings()


@router.get("/test", tags=["health"])
async def test_endpoint() -> dict[str, str]:
    return {"msg": "ok"}


def _player_to_response(player: models.Player) -> PlayerResponse:
    return PlayerResponse(
        player_name=player.player_name,
        telegram_id=player.telegram_id,
        telegram_username=player.telegram_username,
        ip=player.ip,
        code=player.code,
        verified=player.verified,
        password_enabled=player.password_enabled,
        last_verified=player.last_verified,
    )


@router.post("/api/register", response_model=PlayerResponse, tags=["mcverify"])
def register_player(
    payload: RegisterRequest,
    session: Session = Depends(get_db),
) -> PlayerResponse:
    if not verify_telegram_hash(payload.telegram_data.as_flat_dict(), settings.bot_token):
        raise HTTPException(status_code=400, detail="Invalid Telegram hash")

    telegram_user = payload.telegram_data.user
    if telegram_user is None:
        raise HTTPException(status_code=400, detail="Telegram user data is required")

    player = session.scalar(
        select(models.Player).where(
            or_(
                models.Player.telegram_id == telegram_user.id,
                models.Player.code == payload.code,
            )
        )
    )
    now = utcnow()

    if player is None:
        player = models.Player(
            player_name=payload.player_name
            or telegram_user.username
            or f"Player-{telegram_user.id}",
            telegram_id=telegram_user.id,
            telegram_username=telegram_user.username,
            ip=payload.ip,
            code=payload.code,
            verified=True,
            password_enabled=False,
            last_verified=now,
        )
        session.add(player)
    else:
        player.telegram_id = telegram_user.id
        player.telegram_username = telegram_user.username
        player.ip = payload.ip
        if payload.player_name:
            player.player_name = payload.player_name
        if payload.code:
            player.code = payload.code
        player.verified = True
        player.last_verified = now
    session.flush()
    return _player_to_response(player)


@router.post("/api/set_password", response_model=PlayerResponse, tags=["mcverify"])
def set_password(
    payload: PasswordRequest,
    session: Session = Depends(get_db),
) -> PlayerResponse:
    player = session.scalar(
        select(models.Player).where(models.Player.telegram_id == payload.telegram_id)
    )
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    player.password_hash = sha256_hex(payload.password)
    player.password_enabled = True
    session.flush()
    return _player_to_response(player)


@router.post("/api/change_name", response_model=PlayerResponse, tags=["mcverify"])
def change_name(
    payload: ChangeNameRequest,
    session: Session = Depends(get_db),
) -> PlayerResponse:
    player = session.scalar(
        select(models.Player).where(models.Player.telegram_id == payload.telegram_id)
    )
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    session.add(
        models.NameHistory(
            telegram_id=payload.telegram_id,
            old_name=player.player_name,
        )
    )
    player.player_name = payload.new_name
    session.flush()
    return _player_to_response(player)


@router.get("/api/status", response_model=StatusResponse, tags=["mcverify"])
def status(
    player: str = Query(..., description="Minecraft nickname"),
    ip: str = Query(..., description="Player IP address"),
    session: Session = Depends(get_db),
) -> StatusResponse:
    record = session.scalar(select(models.Player).where(models.Player.player_name == player))
    if record is None:
        return StatusResponse(
            verified=False,
            need_reverify=True,
            reason="Player not registered",
        )

    requires_refresh = needs_reverification(record.last_verified, settings.reverify_days)
    if requires_refresh and record.verified:
        record.verified = False
        session.flush()

    if record.ip and record.ip != ip:
        return StatusResponse(
            verified=False,
            need_reverify=True,
            reason="IP changed; re-verification required",
        )

    if not record.verified:
        return StatusResponse(
            verified=False,
            need_reverify=True,
            reason="Verification expired",
        )

    return StatusResponse(
        verified=True,
        need_reverify=requires_refresh,
        reason=None,
    )
