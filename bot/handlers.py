from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from utils.config import get_settings

router = Router(name="base")


def _mini_app_keyboard(code: str | None) -> InlineKeyboardMarkup:
    settings = get_settings()
    webapp_url = settings.backend_url
    if code:
        separator = "&" if "?" in webapp_url else "?"
        webapp_url = f"{webapp_url}{separator}code={code}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть Mini App",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject | None = None) -> None:
    code = command.args if command else None
    greeting = [
        "Привет! Это мини-приложение для верификации Minecraft-аккаунта.",
        "Нажми кнопку ниже, чтобы открыть Mini App.",
    ]
    if code:
        greeting.append(f"Код приглашения: <code>{code}</code>")
    await message.answer(
        "\n".join(greeting),
        reply_markup=_mini_app_keyboard(code),
    )


@router.message(F.text.startswith("/startapp"))
async def startapp(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    code = parts[1] if len(parts) > 1 else None
    await message.answer(
        "Открываю мини-приложение. Если оно не открылось автоматически, нажмите кнопку ниже.",
        reply_markup=_mini_app_keyboard(code),
    )
