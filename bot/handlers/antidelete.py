import logging
from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BusinessMessagesDeleted, Message, User

from ..db import CachedMessage, MessageCache
from ..storage import ConnectionStore

logger = logging.getLogger(__name__)

router = Router(name="antidelete")

_MEDIA_TYPES = ("photo", "video", "voice", "document")


def extract_content(message: Message) -> tuple[str | None, str | None, str | None]:
    """Returns (text, media_type, file_id) for a message."""
    if message.photo:
        return message.caption, "photo", message.photo[-1].file_id
    if message.video:
        return message.caption, "video", message.video.file_id
    if message.voice:
        return message.caption, "voice", message.voice.file_id
    if message.document:
        return message.caption, "document", message.document.file_id
    return message.text, None, None


def sender_display_name(user: User | None) -> str:
    if user is None:
        return "неизвестно"
    if user.username:
        return f"{user.full_name} (@{user.username})"
    return user.full_name


def cache_incoming_message(message: Message, cache: MessageCache) -> None:
    """Called from the business_message handler for messages sent by the chat partner."""
    if message.from_user is None:
        return

    text, media_type, file_id = extract_content(message)
    if text is None and media_type is None:
        return

    cache.save(
        chat_id=message.chat.id,
        message_id=message.message_id,
        sender_id=message.from_user.id,
        sender_name=sender_display_name(message.from_user),
        text=text,
        media_type=media_type,
        file_id=file_id,
        created_at=int(message.date.timestamp()),
    )


def format_deleted_entry(cached: CachedMessage) -> str:
    when = datetime.fromtimestamp(cached.created_at, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "🗑 Удалено\n"
        f"От: {cached.sender_name}\n"
        f"Чат: {cached.chat_id}\n"
        f"Время: {when}\n\n"
        f"{cached.text or ''}"
    )


async def _notify_deleted(bot: Bot, owner_id: int, cached: CachedMessage) -> None:
    caption = format_deleted_entry(cached)

    if cached.media_type in _MEDIA_TYPES and cached.file_id:
        send = getattr(bot, f"send_{cached.media_type}")
        try:
            await send(owner_id, cached.file_id, caption=caption)
            return
        except TelegramBadRequest as e:
            logger.warning("Failed to send deleted media (%s): %s", cached.media_type, e)
            caption = f"{caption}\n\n⚠️ медиа недоступно"

    try:
        await bot.send_message(owner_id, caption)
    except TelegramBadRequest as e:
        logger.warning("Failed to notify owner about deleted message: %s", e)


@router.deleted_business_messages()
async def on_deleted_business_messages(
    event: BusinessMessagesDeleted,
    bot: Bot,
    store: ConnectionStore,
    cache: MessageCache,
) -> None:
    owner_id = store.get_owner(event.business_connection_id)
    if owner_id is None:
        return

    for message_id in event.message_ids:
        cached = cache.get(event.chat.id, message_id)
        if cached is None:
            continue
        cache.mark_deleted(event.chat.id, message_id)
        await _notify_deleted(bot, owner_id, cached)


@router.edited_business_message()
async def on_edited_business_message(
    message: Message,
    bot: Bot,
    store: ConnectionStore,
    cache: MessageCache,
) -> None:
    bcid = message.business_connection_id
    if bcid is None:
        return

    owner_id = store.get_owner(bcid)
    if owner_id is None or message.from_user is None or message.from_user.id == owner_id:
        return  # skip our own edits (typewriter animation) and the owner's own edits

    old = cache.get(message.chat.id, message.message_id)
    old_text = old.text if old else None

    new_text, media_type, file_id = extract_content(message)
    cache.save(
        chat_id=message.chat.id,
        message_id=message.message_id,
        sender_id=message.from_user.id,
        sender_name=sender_display_name(message.from_user),
        text=new_text,
        media_type=media_type,
        file_id=file_id,
        created_at=old.created_at if old else int(message.date.timestamp()),
    )

    text = (
        "✏️ Отредактировано\n"
        f"От: {sender_display_name(message.from_user)}\n"
        f"Чат: {message.chat.id}\n\n"
        f"Было: {old_text or '—'}\n"
        f"Стало: {new_text or '—'}"
    )
    try:
        await bot.send_message(owner_id, text)
    except TelegramBadRequest as e:
        logger.warning("Failed to notify owner about edited message: %s", e)
