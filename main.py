import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Load configuration from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@example_channel")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/example_channel")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

async def is_subscribed(user_id: int) -> bool:
    """Check if the user is subscribed to the channel."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status != "left"
    except Exception:
        # In case of any error consider user as not subscribed
        return False

def subscribe_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Подписаться", url=CHANNEL_LINK),
        InlineKeyboardButton("Проверить", callback_data="check_sub"),
    )
    return keyboard

def main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мой профиль"))
    keyboard.add(KeyboardButton("Пополнить СИМ"))
    keyboard.add(KeyboardButton("Пополнить баланс"))
    keyboard.add(KeyboardButton("Актуальные курсы"))
    return keyboard

async def send_welcome(message: types.Message) -> None:
    user_name = message.from_user.full_name
    await message.answer(
        f"<b>{user_name}</b> Добро пожаловать в «Название бота»",
        reply_markup=main_menu(),
    )

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await send_welcome(message)
    else:
        await message.answer(
            "Пожалуйста, подпишитесь на группу со всеми новостями по кнопке ниже:",
            reply_markup=subscribe_keyboard(),
        )

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def callback_check(callback_query: types.CallbackQuery):
    if await is_subscribed(callback_query.from_user.id):
        await bot.answer_callback_query(callback_query.id)
        await send_welcome(callback_query.message)
    else:
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )

@dp.message_handler(lambda message: message.text == "Мой профиль")
async def my_profile(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return

    purchase_sum = 0  # Placeholder for purchase sum
    username = f"@{message.from_user.username}" if message.from_user.username else "не задан"
    text = (
        f"ID: {message.from_user.id}\n"
        f"Username: {username}\n"
        f"Сумма покупок: {purchase_sum}"
    )
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Архив покупок", callback_data="purchase_history")
    )
    await message.answer(text, reply_markup=kb)

@dp.message_handler(lambda message: message.text in [
    "Пополнить СИМ",
    "Пополнить баланс",
    "Актуальные курсы",
])
async def stub_features(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return

    if message.text == "Пополнить СИМ":
        reply = "Функция будет добавлена позже."
    elif message.text == "Пополнить баланс":
        reply = "Функция будет добавлена позже."
    else:
        reply = "Функция будет добавлена позже."

    await message.answer(reply)

@dp.callback_query_handler(lambda c: c.data == "purchase_history")
async def purchase_history(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Архив покупок пуст.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
