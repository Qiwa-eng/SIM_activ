from aiogram.utils import executor

from loader import dp
from utils import fetch_bot_name
import handlers.start  # noqa: F401
import handlers.topup  # noqa: F401

async def on_startup(dispatcher):
    await fetch_bot_name()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
