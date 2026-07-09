import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

logger = logging.getLogger(__name__)


async def type_out(
    bot: Bot,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
    target_text: str,
    chunk_size: int,
    delay_seconds: float,
) -> None:
    """Progressively reveals target_text via repeated edit_message_text calls."""
    revealed = ""
    for end in range(chunk_size, len(target_text), chunk_size):
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
