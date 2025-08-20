from dataclasses import dataclass
import os


@dataclass
class Settings:
    """Application configuration."""
    bot_token: str


def load_config() -> Settings:
    """Load settings from environment variables."""
    return Settings(bot_token=os.getenv("BOT_TOKEN", ""))
