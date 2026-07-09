import logging

from aiogram import Bot, Router
from aiogram.types import BusinessConnection, Message

from .config import Config
from .storage import ConnectionStore
from .typewriter import type_out

logger = logging.getLogger(__name__)

router = Router(name="business")


@router.business_connection()
async def on_business_connection(
    connection: BusinessConnection, store: ConnectionStore
) -> None:
    if connection.is_enabled:
        store.set(connection.id, connection.user.id)
        logger.info(
            "Business connection %s enabled for owner %s",
            connection.id,
            connection.user.id,
        )
    else:
        store.remove(connection.id)
        logger.info("Business connection %s disabled", connection.id)


@router.business_message()
async def on_business_message(
    message: Message, bot: Bot, store: ConnectionStore, config: Config
) -> None:
    bcid = message.business_connection_id
    if bcid is None or message.text is None:
        return

    owner_id = store.get_owner(bcid)
    if owner_id is None or message.from_user is None or message.from_user.id != owner_id:
        return  # not our own outgoing message - ignore

    text = message.text
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
        chunk_size=config.typewriter_chunk_size,
        delay_seconds=config.typewriter_delay_ms / 1000,
    )
