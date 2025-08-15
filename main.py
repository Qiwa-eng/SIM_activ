import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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

def main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("👤 Мой профиль", callback_data="profile"),
        InlineKeyboardButton("📱 Пополнить СИМ", callback_data="topup_sim"),
        InlineKeyboardButton("💰 Пополнить баланс", callback_data="topup_balance"),
        InlineKeyboardButton("📈 Актуальные курсы", callback_data="rates"),
    )
    return keyboard

def main_menu_text(user_name: str) -> str:
    return f"<b>👋 {user_name}</b>, добро пожаловать в <b>«Название бота»</b>"

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )

async def send_welcome(message: types.Message) -> None:
    user_name = message.from_user.full_name
    await message.answer(
        main_menu_text(user_name),
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

@dp.callback_query_handler(lambda c: c.data == "profile")
async def my_profile(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return

    purchase_sum = 0  # Placeholder for purchase sum
    username = (
        f"@{callback_query.from_user.username}"
        if callback_query.from_user.username
        else "не задан"
    )
    text = (
        "<b>👤 Мой профиль</b>\n"
        f"<b>ID:</b> {callback_query.from_user.id}\n"
        f"<b>Username:</b> {username}\n"
        f"<b>Сумма покупок:</b> {purchase_sum}"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Архив покупок", callback_data="purchase_history"),
        InlineKeyboardButton("🔙 Назад", callback_data="back"),
    )
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in [
    "topup_sim",
    "topup_balance",
    "rates",
])
async def stub_features(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return

    if callback_query.data == "topup_sim":
        reply = "📱 <b>Пополнить СИМ</b>\nФункция будет добавлена позже."
    elif callback_query.data == "topup_balance":
        reply = "💰 <b>Пополнить баланс</b>\nФункция будет добавлена позже."
    else:
        reply = "📈 <b>Актуальные курсы</b>\nФункция будет добавлена позже."

    kb = back_keyboard()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(reply, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "purchase_history")
async def purchase_history(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    kb = back_keyboard()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text("Архив покупок пуст.", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(
        main_menu_text(callback_query.from_user.full_name),
        reply_markup=main_menu(),
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
