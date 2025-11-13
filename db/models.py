from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    telegram_username: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(Text, unique=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text)
    password_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_verified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class NameHistory(Base):
    __tablename__ = "name_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    old_name: Mapped[str] = mapped_column(Text, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
