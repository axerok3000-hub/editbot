import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    owner_id: int
    connections_file: str
    excluded_chats_file: str
    cache_db_file: str
    cache_retention_days: int


def load_config() -> Config:
    bot_token = os.environ["BOT_TOKEN"]
    owner_id = int(os.environ["OWNER_ID"])
    return Config(
        bot_token=bot_token,
        owner_id=owner_id,
        connections_file=os.environ.get("CONNECTIONS_FILE", "storage/connections.json"),
        excluded_chats_file=os.environ.get(
            "EXCLUDED_CHATS_FILE", "storage/excluded_chats.json"
        ),
        cache_db_file=os.environ.get("CACHE_DB_FILE", "storage/cache.db"),
        cache_retention_days=int(os.environ.get("CACHE_RETENTION_DAYS", "7")),
    )
