import logging
import time

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from .db import SettingsStore
from .styles import DEFAULT_STYLE, apply_style

logger = logging.getLogger(__name__)

MIN_EDIT_INTERVAL_SECONDS = 0.5

_last_edit_at: dict[int, float] = {}


def _is_rate_limited(chat_id: int) -> bool:
    """Self-imposed throttle: at most one style edit per chat per 0.5s."""
    now = time.monotonic()
    last = _last_edit_at.get(chat_id)
    if last is not None and now - last < MIN_EDIT_INTERVAL_SECONDS:
        return True
    _last_edit_at[chat_id] = now
    return False


async def apply_style_to_message(
    bot: Bot,
    settings: SettingsStore,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
    text: str,
    style: str,
    owner_id: int,
) -> None:
    if _is_rate_limited(chat_id):
        return  # skip this edit silently to stay under the self-imposed limit

    rendered, parse_mode = apply_style(text, style)

    try:
        await bot.edit_message_text(
            text=rendered,
            business_connection_id=business_connection_id,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
        )
    except TelegramRetryAfter as e:
        settings.set_style(owner_id, DEFAULT_STYLE)
        logger.warning(
            "Style disabled for owner %s after flood control (retry_after=%s)",
            owner_id,
            e.retry_after,
        )
        try:
            await bot.send_message(
                owner_id,
                "⚠️ Стиль сообщений временно отключён — Telegram ограничил "
                f"частоту правок (подожди {e.retry_after} сек). "
                "Включить заново можно через /style.",
            )
        except TelegramBadRequest as notify_error:
            logger.warning("Failed to notify owner about disabled style: %s", notify_error)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        logger.warning("Failed to apply style to message %s: %s", message_id, e)
