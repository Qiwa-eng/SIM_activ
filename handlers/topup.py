from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, bot, ADMIN_ID
from utils import is_subscribed
from keyboards import (
    subscribe_keyboard,
    back_keyboard,
    operators_keyboard,
)
from db import (
    get_balance,
    deduct_balance,
    add_balance,
    add_invoice,
    get_invoice as db_get_invoice,
    remove_invoice,
    add_purchase,
    update_purchase_status,
    get_purchase_by_id,
    is_topup_enabled,
    is_operator_enabled,
    is_banned,
    ensure_user,
)
from crypto_pay import create_invoice, get_invoice as crypto_get_invoice

class TopupSim(StatesGroup):
    waiting_for_phone = State()
    waiting_for_operator = State()
    waiting_for_amount = State()

class TopupBalance(StatesGroup):
    waiting_for_amount = State()

@dp.callback_query_handler(lambda c: c.data == "topup_sim")
async def topup_sim_start(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if is_banned(user_id):
        await callback_query.answer("Вы забанены", show_alert=True)
        return
    if not await is_subscribed(user_id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    if not is_topup_enabled():
        await callback_query.message.answer("Пополнения временно остановлены.")
        await callback_query.answer()
        return
    ensure_user(user_id)
    await callback_query.answer()
    await callback_query.message.answer("Введите ваш номер:")
    await TopupSim.waiting_for_phone.set()

@dp.message_handler(state=TopupSim.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "Выберите оператора:", reply_markup=operators_keyboard()
    )
    await TopupSim.waiting_for_operator.set()

@dp.callback_query_handler(lambda c: c.data.startswith("op_"), state=TopupSim.waiting_for_operator)
async def process_operator(callback_query: types.CallbackQuery, state: FSMContext):
    operator = callback_query.data.split("_", 1)[1]
    if not is_operator_enabled(operator):
        await callback_query.message.answer("Пополнение по данному оператору недоступно.")
        await callback_query.answer()
        await state.finish()
        return
    await state.update_data(operator=operator)
    await callback_query.message.answer("Введите сумму пополнения (в $):")
    await callback_query.answer()
    await TopupSim.waiting_for_amount.set()

@dp.message_handler(state=TopupSim.waiting_for_amount)
async def process_amount_sim(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректную сумму:")
        return
    user_id = message.from_user.id
    data = await state.get_data()
    phone = data.get("phone")
    operator = data.get("operator")
    balance = get_balance(user_id)
    if balance >= amount:
        deduct_balance(user_id, amount)
        add_purchase(user_id, {
            "phone": phone,
            "operator": operator,
            "amount": amount,
            "status": "completed",
        })
        await message.answer("СИМ успешно пополнена.", reply_markup=back_keyboard())
    else:
        invoice = await create_invoice(amount)
        if invoice.get("ok"):
            result = invoice["result"]
            url = result.get("pay_url", "")
            invoice_id = result.get("invoice_id")
            add_invoice(invoice_id, {
                "type": "sim",
                "user_id": user_id,
                "phone": phone,
                "operator": operator,
                "amount": amount,
            })
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("Я оплатил", callback_data=f"check_invoice_{invoice_id}"),
                InlineKeyboardButton("🔙 Назад", callback_data="back"),
            )
            await message.answer(
                f"Недостаточно средств. Оплатите счёт: {url}",
                reply_markup=kb,
            )
        else:
            await message.answer(
                "Не удалось создать счёт на оплату.",
                reply_markup=back_keyboard(),
            )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "topup_balance")
async def topup_balance_start(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if is_banned(user_id):
        await callback_query.answer("Вы забанены", show_alert=True)
        return
    if not await is_subscribed(user_id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
    if not is_topup_enabled():
        await callback_query.message.answer("Пополнения временно остановлены.")
        await callback_query.answer()
        return
    ensure_user(user_id)
    await callback_query.answer()
    await callback_query.message.answer("Введите сумму пополнения баланса (в $):")
    await TopupBalance.waiting_for_amount.set()

@dp.message_handler(state=TopupBalance.waiting_for_amount)
async def process_amount_balance(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректную сумму:")
        return
    invoice = await create_invoice(amount)
    if invoice.get("ok"):
        result = invoice["result"]
        url = result.get("pay_url", "")
        invoice_id = result.get("invoice_id")
        add_invoice(invoice_id, {
            "type": "balance",
            "user_id": message.from_user.id,
            "amount": amount,
        })
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("Я оплатил", callback_data=f"check_invoice_{invoice_id}"),
            InlineKeyboardButton("🔙 Назад", callback_data="back"),
        )
        await message.answer(
            f"Оплатите счёт для пополнения баланса: {url}",
            reply_markup=kb,
        )
    else:
        await message.answer(
            "Не удалось создать счёт на оплату.",
            reply_markup=back_keyboard(),
        )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("check_invoice_"))
async def check_invoice_callback(callback_query: types.CallbackQuery):
    invoice_id = int(callback_query.data.split("_", 2)[2])
    info = db_get_invoice(invoice_id)
    if not info:
        await callback_query.answer("Счёт не найден", show_alert=True)
        return
    invoice = await crypto_get_invoice(invoice_id)
    if invoice and invoice.get("status") == "paid":
        remove_invoice(invoice_id)
        user_id = info["user_id"]
        amount = info["amount"]
        if info["type"] == "balance":
            add_balance(user_id, amount)
            await callback_query.message.answer(f"Баланс пополнен на {amount} $")
        else:
            purchase_id = add_purchase(user_id, {
                "phone": info["phone"],
                "operator": info["operator"],
                "amount": amount,
                "status": "pending",
            })
            text = (
                f"Пользователь: {user_id}\n"
                f"Номер: {info['phone']}\n"
                f"Оператор: {info['operator']}\n"
                f"Сумма: {amount} $"
            )
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("Пополнено", callback_data=f"admin_confirm_{purchase_id}"),
                InlineKeyboardButton("Отмена", callback_data=f"admin_cancel_{purchase_id}"),
            )
            await bot.send_message(ADMIN_ID, text, reply_markup=kb)
            await callback_query.message.answer("Платёж получен, ожидайте пополнения")
        await callback_query.answer()
    else:
        await callback_query.answer("Платёж не найден", show_alert=True)


@dp.callback_query_handler(lambda c: c.data.startswith("admin_confirm_"))
async def admin_confirm(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 2)[2])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "completed")
    await bot.send_message(
        purchase["user_id"],
        f"Ваш номер {purchase['phone']} пополнен на {purchase['amount']} $",
    )
    await callback_query.message.edit_text("Помечено как пополнено")
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("admin_cancel_"))
async def admin_cancel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 2)[2])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "canceled")
    add_balance(purchase["user_id"], purchase["amount"])
    await bot.send_message(
        purchase["user_id"],
        f"Пополнение отменено, {purchase['amount']} $ возвращено на баланс",
    )
    await callback_query.message.edit_text("Отменено и возвращено")
    await callback_query.answer()
