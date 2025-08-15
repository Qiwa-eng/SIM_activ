from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import subscribe_keyboard, main_menu, back_keyboard
from utils import is_subscribed, main_menu_text
from db import get_balance, ensure_user, is_banned, get_user_purchases

router = Router()

async def send_welcome(message: types.Message) -> None:
    user_name = message.from_user.full_name
    await message.answer(
        main_menu_text(user_name),
        reply_markup=main_menu(),
    )

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    ensure_user(user_id)
    if is_banned(user_id):
        await message.answer("Вы забанены")
        return
    if await is_subscribed(user_id):
        await send_welcome(message)
    else:
        await message.answer(
            "Пожалуйста, подпишитесь на группу со всеми новостями по кнопке ниже:",
            reply_markup=subscribe_keyboard(),
        )

@router.callback_query(F.data == "check_sub")
async def callback_check(callback_query: types.CallbackQuery):
    if await is_subscribed(callback_query.from_user.id):
        await callback_query.answer()
        await send_welcome(callback_query.message)
    else:
        await callback_query.answer()
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )

@router.callback_query(F.data == "profile")
async def my_profile(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return

    purchase_sum = 0
    balance = get_balance(callback_query.from_user.id)
    username = (
        f"@{callback_query.from_user.username}"
        if callback_query.from_user.username
        else "не задан"
    )
    text = (
        "<b>👤 Мой профиль</b>\n"
        f"<b>ID:</b> {callback_query.from_user.id}\n"
        f"<b>Username:</b> {username}\n"
        f"<b>Сумма покупок:</b> {purchase_sum}\n"
        f"<b>Баланс:</b> {balance} $"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Архив покупок", callback_data="purchase_history"),
        InlineKeyboardButton("🔙 Назад", callback_data="back"),
    )
    await callback_query.answer()
    await callback_query.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "purchase_history")
async def purchase_history(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    purchases = get_user_purchases(callback_query.from_user.id)
    text = (
        "Архив покупок пуст." if not purchases else "\n".join(
            [
                f"#{p['id']} {p.get('operator','-')} {p.get('phone','-')} {p['amount']}$ {p['status']}"
                for p in purchases
            ]
        )
    )
    kb = back_keyboard()
    await callback_query.answer()
    await callback_query.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "rates")
async def rates(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    kb = back_keyboard()
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📈 <b>Актуальные курсы</b>\nФункция будет добавлена позже.",
        reply_markup=kb,
    )

@router.callback_query(F.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    await callback_query.answer()
    await callback_query.message.edit_text(
        main_menu_text(callback_query.from_user.full_name),
        reply_markup=main_menu(),
    )
