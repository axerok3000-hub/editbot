import asyncio
import logging
import random
import re
import time
from collections import deque

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from .fonts import FONTS
from .typewriter import type_out as typewriter

logger = logging.getLogger(__name__)

SUFFIX_PATTERN = re.compile(r"\.([prhsf])$")

MAX_ANIMATED_LENGTH = 120
LONG_TEXT_WARNING = (
    f"⚠️ Текст слишком длинный для эффекта (>{MAX_ANIMATED_LENGTH} символов) — "
    "отправлен без анимации."
)

GLOBAL_RATE_LIMIT = 6
GLOBAL_RATE_WINDOW_SECONDS = 60
RATE_LIMIT_WARNING = "⚠️ Слишком много эффектов подряд (лимит 6/мин) — этот пропущен."

MARQUEE_MAX_STEPS = 15
MARQUEE_DELAY = 0.6

GLITCH_CHARS = "̶̷̸#@%&$"
GLITCH_RATIO = 0.3
GLITCH_ITERATIONS = 3
GLITCH_DELAY = 0.5

PULSE_DELAY = 0.5

# chat_ids with a currently running effect - enforces "one active animation per chat"
_active_chats: set[int] = set()
# rolling window of effect start timestamps - enforces the global 6/min limit
_global_starts: deque[float] = deque()


def parse_effect_suffix(text: str) -> tuple[str, str] | None:
    """Returns (target_text, effect_key) if text ends with a recognized effect suffix."""
    match = SUFFIX_PATTERN.search(text)
    if not match:
        return None
    target_text = text[: match.start()]
    if not target_text:
        return None
    return target_text, match.group(1)


def _global_rate_limited() -> bool:
    now = time.monotonic()
    while _global_starts and now - _global_starts[0] > GLOBAL_RATE_WINDOW_SECONDS:
        _global_starts.popleft()
    if len(_global_starts) >= GLOBAL_RATE_LIMIT:
        return True
    _global_starts.append(now)
    return False


async def _edit(bot: Bot, business_connection_id: str, chat_id: int, message_id: int, text: str) -> None:
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
        logger.warning("Effect edit failed for message %s: %s", message_id, e)


async def _warn_owner(bot: Bot, owner_id: int, text: str) -> None:
    try:
        await bot.send_message(owner_id, text)
    except TelegramBadRequest as e:
        logger.warning("Failed to notify owner: %s", e)


async def marquee(
    bot: Bot, business_connection_id: str, chat_id: int, message_id: int, target_text: str, owner_id: int
) -> None:
    """.r - cyclic shift of the text, marquee-style."""
    length = len(target_text)
    steps = min(length, MARQUEE_MAX_STEPS)
    last_shown = target_text
    for i in range(1, steps + 1):
        last_shown = target_text[i:] + target_text[:i]
        await _edit(bot, business_connection_id, chat_id, message_id, last_shown)
        await asyncio.sleep(MARQUEE_DELAY)
    if last_shown != target_text:
        await _edit(bot, business_connection_id, chat_id, message_id, target_text)


def _glitched(text: str) -> str:
    chars = list(text)
    if not chars:
        return text
    count = max(1, round(len(chars) * GLITCH_RATIO))
    indices = random.sample(range(len(chars)), min(count, len(chars)))
    for i in indices:
        chars[i] = random.choice(GLITCH_CHARS)
    return "".join(chars)


async def glitch(
    bot: Bot, business_connection_id: str, chat_id: int, message_id: int, target_text: str, owner_id: int
) -> None:
    """.h - a few iterations of randomly corrupted text, then the clean text."""
    for _ in range(GLITCH_ITERATIONS):
        await _edit(bot, business_connection_id, chat_id, message_id, _glitched(target_text))
        await asyncio.sleep(GLITCH_DELAY)
    await _edit(bot, business_connection_id, chat_id, message_id, target_text)


async def pulse(
    bot: Bot, business_connection_id: str, chat_id: int, message_id: int, target_text: str, owner_id: int
) -> None:
    """.s - alternates between normal and upper case a couple of times."""
    sequence = [target_text.upper(), target_text, target_text.upper(), target_text]
    for state in sequence:
        await _edit(bot, business_connection_id, chat_id, message_id, state)
        await asyncio.sleep(PULSE_DELAY)


async def instant_font(
    bot: Bot, business_connection_id: str, chat_id: int, message_id: int, target_text: str, owner_id: int
) -> None:
    """.f - one-shot random font from fonts.py, no animation."""
    style = random.choice(list(FONTS.keys()))
    await _edit(bot, business_connection_id, chat_id, message_id, FONTS[style](target_text))


EFFECTS = {
    "p": typewriter,
    "r": marquee,
    "h": glitch,
    "s": pulse,
    "f": instant_font,
}


async def apply_effect(
    bot: Bot,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
    target_text: str,
    effect_key: str,
    owner_id: int,
) -> None:
    effect_fn = EFFECTS.get(effect_key)
    if effect_fn is None:
        return

    if chat_id in _active_chats:
        return  # one active animation per chat - skip silently

    if _global_rate_limited():
        await _warn_owner(bot, owner_id, RATE_LIMIT_WARNING)
        return

    _active_chats.add(chat_id)
    try:
        if len(target_text) > MAX_ANIMATED_LENGTH:
            await _edit(bot, business_connection_id, chat_id, message_id, target_text)
            await _warn_owner(bot, owner_id, LONG_TEXT_WARNING)
            return

        await effect_fn(
            bot=bot,
            business_connection_id=business_connection_id,
            chat_id=chat_id,
            message_id=message_id,
            target_text=target_text,
            owner_id=owner_id,
        )
    finally:
        _active_chats.discard(chat_id)
