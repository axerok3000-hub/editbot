import asyncio
import logging
import time

from aiogram import Bot, Dispatcher

from bot.config import load_config
from bot.db import MessageCache
from bot.handlers import antidelete, business, commands
from bot.storage import ConnectionStore, ExcludedChatsStore

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_SECONDS = 3600


async def _cleanup_loop(cache: MessageCache, retention_days: int) -> None:
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        cutoff = int(time.time()) - retention_days * 24 * 3600
        removed = cache.purge_older_than(cutoff)
        if removed:
            logger.info("Purged %d cached messages older than %d days", removed, retention_days)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    store = ConnectionStore(config.connections_file)
    excluded_chats = ExcludedChatsStore(config.excluded_chats_file)
    cache = MessageCache(config.cache_db_file)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(store=store, excluded_chats=excluded_chats, cache=cache, config=config)
    dp.include_router(commands.router)
    dp.include_router(business.router)
    dp.include_router(antidelete.router)

    asyncio.create_task(_cleanup_loop(cache, config.cache_retention_days))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
