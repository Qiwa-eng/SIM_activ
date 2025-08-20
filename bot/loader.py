from aiogram import Bot, Dispatcher

from bot.config import load_config


config = load_config()
bot = Bot(token=config.bot_token, parse_mode="HTML")
dp = Dispatcher()
