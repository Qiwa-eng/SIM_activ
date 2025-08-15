from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp
from utils import is_subscribed
from keyboards import (
    subscribe_keyboard,
    back_keyboard,
    operators_keyboard,
)
from db import get_balance, deduct_balance
from crypto_pay import create_invoice

class TopupSim(StatesGroup):
    waiting_for_phone = State()
    waiting_for_operator = State()
    waiting_for_amount = State()

class TopupBalance(StatesGroup):
    waiting_for_amount = State()

@dp.callback_query_handler(lambda c: c.data == "topup_sim")
async def topup_sim_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
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
    balance = get_balance(message.from_user.id)
    if balance >= amount:
        deduct_balance(message.from_user.id, amount)
        await message.answer("СИМ успешно пополнена.", reply_markup=back_keyboard())
    else:
        invoice = await create_invoice(amount)
        if invoice.get("ok"):
            url = invoice["result"].get("pay_url", "")
            await message.answer(
                f"Недостаточно средств. Оплатите счёт: {url}",
                reply_markup=back_keyboard(),
            )
        else:
            await message.answer(
                "Не удалось создать счёт на оплату.",
                reply_markup=back_keyboard(),
            )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "topup_balance")
async def topup_balance_start(callback_query: types.CallbackQuery):
    if not await is_subscribed(callback_query.from_user.id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:",
            reply_markup=subscribe_keyboard(),
        )
        return
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
        url = invoice["result"].get("pay_url", "")
        await message.answer(
            f"Оплатите счёт для пополнения баланса: {url}",
            reply_markup=back_keyboard(),
        )
    else:
        await message.answer(
            "Не удалось создать счёт на оплату.",
            reply_markup=back_keyboard(),
        )
    await state.finish()
