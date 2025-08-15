from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from loader import ADMIN_ID, bot
from keyboards import admin_keyboard, topup_control_keyboard
from db import (
    set_ban,
    is_banned,
    get_all_users,
    get_all_purchases,
    is_topup_enabled,
    set_topup_enabled,
    disable_operator,
    enable_operator,
    is_operator_enabled,
)

router = Router()


class Broadcast(StatesGroup):
    waiting_for_content = State()


class BanUser(StatesGroup):
    waiting_for_user_id = State()


class OperatorControl(StatesGroup):
    waiting_for_name = State()


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Админ панель", reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    await callback_query.message.answer("Отправьте сообщение или фото для рассылки:")
    await state.set_state(Broadcast.waiting_for_content)
    await callback_query.answer()


@router.message(Broadcast.waiting_for_content, content_types=types.ContentTypes.ANY)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        caption = message.caption or ""
        for uid in users:
            try:
                await bot.send_photo(uid, file_id, caption)
            except Exception:
                pass
    else:
        text = message.text or ""
        for uid in users:
            try:
                await bot.send_message(uid, text)
            except Exception:
                pass
    await message.answer("Рассылка завершена", reply_markup=admin_keyboard())
    await state.clear()


@router.callback_query(F.data == "admin_ban")
async def admin_ban_start(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    await callback_query.message.answer("Введите ID пользователя:")
    await state.set_state(BanUser.waiting_for_user_id)
    await callback_query.answer()


@router.message(BanUser.waiting_for_user_id)
async def process_ban(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("Введите корректный ID:")
        return
    if is_banned(user_id):
        set_ban(user_id, False)
        await message.answer("Пользователь разбанен", reply_markup=admin_keyboard())
    else:
        set_ban(user_id, True)
        await message.answer("Пользователь забанен", reply_markup=admin_keyboard())
    await state.clear()


@router.callback_query(F.data == "admin_purchases")
async def admin_purchases(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchases = get_all_purchases()
    if not purchases:
        text = "Покупок нет."
    else:
        text = "\n".join(
            [
                f"#{p['id']} user {p['user_id']} {p.get('operator', '-')} {p.get('phone', '-')} {p['amount']}$ {p['status']}"
                for p in purchases
            ]
        )
    await callback_query.message.answer(text)
    await callback_query.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    users = get_all_users()
    text = "Всего пользователей: {}\n{}".format(len(users), "\n".join(map(str, users)))
    await callback_query.message.answer(text)
    await callback_query.answer()


@router.callback_query(F.data == "admin_topups")
async def admin_topups(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    enabled = is_topup_enabled()
    await callback_query.message.answer(
        "Управление пополнениями", reply_markup=topup_control_keyboard(enabled)
    )
    await callback_query.answer()


@router.callback_query(F.data == "topup_stop_all")
async def topup_stop_all(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    set_topup_enabled(False)
    await callback_query.message.answer("Пополнения остановлены", reply_markup=admin_keyboard())
    await callback_query.answer()


@router.callback_query(F.data == "topup_enable_all")
async def topup_enable_all(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    set_topup_enabled(True)
    await callback_query.message.answer("Пополнения возобновлены", reply_markup=admin_keyboard())
    await callback_query.answer()


@router.callback_query(F.data == "topup_toggle_operator")
async def topup_toggle_operator(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    await callback_query.message.answer("Введите название оператора:")
    await state.set_state(OperatorControl.waiting_for_name)
    await callback_query.answer()


@router.message(OperatorControl.waiting_for_name)
async def process_operator_toggle(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    op = message.text.strip()
    if is_operator_enabled(op):
        disable_operator(op)
        await message.answer(
            f"Оператор {op} отключен", reply_markup=admin_keyboard()
        )
    else:
        enable_operator(op)
        await message.answer(
            f"Оператор {op} включен", reply_markup=admin_keyboard()
        )
    await state.clear()
