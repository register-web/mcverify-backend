from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramInitData(BaseModel):
    user: Optional[TelegramUser] = None
    hash: str
    auth_date: Optional[int] = None
    query_id: Optional[str] = None
    start_param: Optional[str] = Field(default=None, alias="start_param")

    class Config:
        extra = "allow"

    def as_flat_dict(self) -> Dict[str, Any]:
        data = self.dict(by_alias=True)
        return data


class RegisterRequest(BaseModel):
    telegram_data: TelegramInitData
    code: str
    ip: str
    player_name: Optional[str] = None


class PasswordRequest(BaseModel):
    telegram_id: int
    password: str


class ChangeNameRequest(BaseModel):
    telegram_id: int
    new_name: str


class PlayerResponse(BaseModel):
    player_name: str
    telegram_id: Optional[int]
    telegram_username: Optional[str]
    ip: Optional[str]
    code: Optional[str]
    verified: bool
    password_enabled: bool
    last_verified: Optional[datetime]


class StatusResponse(BaseModel):
    verified: bool
    need_reverify: bool
    reason: Optional[str]
