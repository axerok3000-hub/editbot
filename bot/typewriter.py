import asyncio
import logging
import math

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

logger = logging.getLogger(__name__)

SHORT_TEXT_LIMIT = 20
SHORT_TEXT_DELAY = 0.4

MEDIUM_TEXT_LIMIT = 120
MEDIUM_TEXT_DELAY = 0.6
MEDIUM_TEXT_MAX_STEPS = 18

LONG_TEXT_WARNING = (
    "⚠️ Текст слишком длинный для анимации печати "
    f"(>{MEDIUM_TEXT_LIMIT} символов) — отправлен без эффекта."
)


async def type_out(
    bot: Bot,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
    target_text: str,
    owner_id: int,
) -> None:
    """Progressively reveals target_text via repeated edit_message_text calls.

    Speed adapts to length: short texts type out one character at a time,
    medium texts are capped at a fixed number of steps, and long texts skip
    the animation entirely (with a DM warning to the owner).
    """
    length = len(target_text)

    if length > MEDIUM_TEXT_LIMIT:
        await _edit(bot, business_connection_id, chat_id, message_id, target_text)
        await _warn_owner(bot, owner_id)
        return

    if length <= SHORT_TEXT_LIMIT:
        chunk_size = 1
        delay_seconds = SHORT_TEXT_DELAY
    else:
        chunk_size = math.ceil(length / MEDIUM_TEXT_MAX_STEPS)
        delay_seconds = MEDIUM_TEXT_DELAY

    revealed = ""
    for end in range(chunk_size, length, chunk_size):
        revealed = target_text[:end]
        await _edit(bot, business_connection_id, chat_id, message_id, revealed)
        await asyncio.sleep(delay_seconds)

    if revealed != target_text:
        await _edit(bot, business_connection_id, chat_id, message_id, target_text)


async def _edit(
    bot: Bot,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
    text: str,
) -> None:
    try:
        await bot.edit_message_text(
            text=text,
            business_connection_id=business_connection_id,
            chat_id=chat_id,
            message_id=message_id,
        )
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await _edit(bot, business_connection_id, chat_id, message_id, text)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        logger.warning("Failed to edit business message %s: %s", message_id, e)


async def _warn_owner(bot: Bot, owner_id: int) -> None:
    try:
        await bot.send_message(owner_id, LONG_TEXT_WARNING)
    except TelegramBadRequest as e:
        logger.warning("Failed to warn owner %s about long text: %s", owner_id, e)
