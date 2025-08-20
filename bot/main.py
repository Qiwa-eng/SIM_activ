import asyncio

from .handlers import register_handlers
from .loader import bot, dp


def main() -> None:
    """Entrypoint for running the bot."""
    register_handlers(dp)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
