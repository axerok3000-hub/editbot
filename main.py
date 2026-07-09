import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import load_config
from bot.handlers import router
from bot.storage import ConnectionStore


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    store = ConnectionStore(config.connections_file)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(store=store, config=config)
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
