import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    typewriter_suffix: str
    typewriter_chunk_size: int
    typewriter_delay_ms: int
    connections_file: str


def load_config() -> Config:
    bot_token = os.environ["BOT_TOKEN"]
    return Config(
        bot_token=bot_token,
        typewriter_suffix=os.environ.get("TYPEWRITER_SUFFIX", ".p"),
        typewriter_chunk_size=int(os.environ.get("TYPEWRITER_CHUNK_SIZE", "2")),
        typewriter_delay_ms=int(os.environ.get("TYPEWRITER_DELAY_MS", "250")),
        connections_file=os.environ.get("CONNECTIONS_FILE", "storage/connections.json"),
    )
