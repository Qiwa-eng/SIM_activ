import asyncio

from app.loader import bot, dp
from app.utils import fetch_bot_name
from app.handlers import start, topup, admin


async def main() -> None:
    dp.include_router(start.router)
    dp.include_router(topup.router)
    dp.include_router(admin.router)
    await fetch_bot_name()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
