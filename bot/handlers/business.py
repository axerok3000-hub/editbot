import logging

from aiogram import Bot, Router
from aiogram.types import BusinessConnection, Message

from ..config import Config
from ..db import MessageCache
from ..storage import ConnectionStore, ExcludedChatsStore
from ..typewriter import type_out
from .antidelete import cache_incoming_message

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
    config: Config,
) -> None:
    bcid = message.business_connection_id
    if bcid is None:
        return

    owner_id = store.get_owner(bcid)
    if owner_id is None or message.from_user is None:
        return

    if message.from_user.id != owner_id:
        cache_incoming_message(message, cache)  # message from the chat partner - track for anti-delete
        return

    if excluded_chats.is_excluded(message.chat.id):
        return

    text = message.text
    if text is None:
        return
    suffix = config.typewriter_suffix
    if not text.endswith(suffix):
        return

    target_text = text[: -len(suffix)]
    if not target_text:
        return

    await type_out(
        bot=bot,
        business_connection_id=bcid,
        chat_id=message.chat.id,
        message_id=message.message_id,
        target_text=target_text,
        owner_id=owner_id,
    )
