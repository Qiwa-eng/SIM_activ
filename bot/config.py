from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application configuration."""
    bot_token: str


def load_config() -> Settings:
    """Load settings from environment variables."""
    return Settings(bot_token=os.getenv("BOT_TOKEN", ""))
