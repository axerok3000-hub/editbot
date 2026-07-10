import logging

from aiogram import Bot, Router
from aiogram.types import BusinessConnection, Message

from ..db import KnownChatsStore, MessageCache, SettingsStore
from ..effects import apply_effect, parse_effect_suffix
from ..storage import ConnectionStore, ExcludedChatsStore
from ..style_apply import apply_style_to_message
from ..styles import DEFAULT_STYLE
from .antidelete import cache_incoming_message, sender_display_name

logger = logging.getLogger(__name__)

router = Router(name="business")


@router.business_connection()
async def on_business_connection(
    connection: BusinessConnection, store: ConnectionStore
) -> None:
    store.set(
        connection.id,
        connection.user.id,
        connection.is_enabled,
        connected_at=int(connection.date.timestamp()),
    )
    logger.info(
        "Business connection %s for owner %s, is_enabled=%s",
        connection.id,
        connection.user.id,
        connection.is_enabled,
    )


@router.business_message()
async def on_business_message(
    message: Message,
    bot: Bot,
    store: ConnectionStore,
    excluded_chats: ExcludedChatsStore,
    cache: MessageCache,
    settings: SettingsStore,
    known_chats: KnownChatsStore,
) -> None:
    bcid = message.business_connection_id
    if bcid is None:
        return

    owner_id = store.get_owner(bcid)
    if owner_id is None or message.from_user is None:
        return

    if message.from_user.id != owner_id:
        known_chats.touch(message.chat.id, sender_display_name(message.from_user))
        cache_incoming_message(message, cache)  # message from the chat partner - track for anti-delete
        return

    known_chats.touch(message.chat.id, display_name=None)  # keep last_seen fresh, don't clobber label

    if excluded_chats.is_excluded(message.chat.id):
        return

    text = message.text
    if text is None:
        return

    parsed = parse_effect_suffix(text)
    if parsed is not None:
        target_text, effect_key = parsed
        await apply_effect(
            bot=bot,
            business_connection_id=bcid,
            chat_id=message.chat.id,
            message_id=message.message_id,
            target_text=target_text,
            effect_key=effect_key,
            owner_id=owner_id,
        )
        return

    style = settings.get_style(owner_id)
    if style == DEFAULT_STYLE:
        return

    await apply_style_to_message(
        bot=bot,
        settings=settings,
        business_connection_id=bcid,
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        style=style,
        owner_id=owner_id,
    )
