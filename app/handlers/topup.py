from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.loader import bot, ADMIN_ID
from app.utils import is_subscribed
from app.keyboards import subscribe_keyboard, back_keyboard, operators_keyboard
from data.db import (
    add_balance,
    add_purchase,
    update_purchase_status,
    get_purchase_by_id,
    is_topup_enabled,
    is_operator_enabled,
    is_banned,
    ensure_user,
)

router = Router()


class TopupSim(StatesGroup):
    waiting_for_phone = State()
    waiting_for_operator = State()
    waiting_for_receipt = State()


class TopupBalance(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()


@router.callback_query(F.data == "topup_sim")
async def topup_sim_start(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if is_banned(user_id):
        await callback_query.answer("Вы забанены", show_alert=True)
        return
    if not await is_subscribed(user_id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:", reply_markup=subscribe_keyboard()
        )
        return
    if not is_topup_enabled():
        await callback_query.message.answer("Пополнения временно остановлены.")
        await callback_query.answer()
        return
    ensure_user(user_id)
    await callback_query.answer()
    await callback_query.message.answer("Введите ваш номер:")
    await state.set_state(TopupSim.waiting_for_phone)


@router.message(F.text == "📱 Пополнить СИМ")
async def topup_sim_start_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_banned(user_id):
        await message.answer("Вы забанены")
        return
    if not await is_subscribed(user_id):
        await message.answer(
            "Пожалуйста, подпишитесь на канал:", reply_markup=subscribe_keyboard()
        )
        return
    if not is_topup_enabled():
        await message.answer("Пополнения временно остановлены.")
        return
    ensure_user(user_id)
    await message.answer("Введите ваш номер:")
    await state.set_state(TopupSim.waiting_for_phone)


@router.message(TopupSim.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Выберите оператора:", reply_markup=operators_keyboard())
    await state.set_state(TopupSim.waiting_for_operator)


@router.callback_query(F.data.startswith("op_"), TopupSim.waiting_for_operator)
async def process_operator(callback_query: types.CallbackQuery, state: FSMContext):
    operator = callback_query.data.split("_", 1)[1]
    if not is_operator_enabled(operator):
        await callback_query.message.answer("Пополнение по данному оператору недоступно.")
        await callback_query.answer()
        await state.clear()
        return
    await state.update_data(operator=operator)
    await callback_query.message.answer(
        "Пожалуйста, отправьте чек с суммой, на сколько нужно пополнить номер"
    )
    await callback_query.answer()
    await state.set_state(TopupSim.waiting_for_receipt)


@router.message(TopupSim.waiting_for_receipt, content_types=types.ContentTypes.ANY)
async def process_receipt_sim(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    phone = data.get("phone")
    operator = data.get("operator")

    receipt_id = None
    caption = message.caption or message.text or ""
    try:
        amount = float(caption.replace(",", ".")) if caption else 0.0
    except ValueError:
        amount = 0.0

    if message.photo:
        receipt_id = message.photo[-1].file_id
    elif message.document:
        receipt_id = message.document.file_id
    else:
        receipt_id = caption

    purchase_id = add_purchase(
        user_id,
        {
            "type": "sim",
            "phone": phone,
            "operator": operator,
            "amount": amount,
            "receipt": receipt_id,
            "status": "pending",
        },
    )

    text = (
        f"Пользователь: {user_id}\n"
        f"Номер: {phone}\n"
        f"Оператор: {operator}\n"
        f"Сумма: {amount}" + ("" if message.photo or message.document else f"\nСсылка на чек: {receipt_id}")
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("В обработке", callback_data=f"processing_{purchase_id}"),
        InlineKeyboardButton("Отменить обработку", callback_data=f"cancel_{purchase_id}"),
    )
    if message.photo:
        await bot.send_photo(ADMIN_ID, receipt_id, caption=text, reply_markup=kb)
    elif message.document:
        await bot.send_document(ADMIN_ID, receipt_id, caption=text, reply_markup=kb)
    else:
        await bot.send_message(ADMIN_ID, text, reply_markup=kb)

    await message.answer("Запрос отправлен администратору", reply_markup=back_keyboard())
    await state.clear()


@router.callback_query(F.data == "topup_balance")
async def topup_balance_start(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if is_banned(user_id):
        await callback_query.answer("Вы забанены", show_alert=True)
        return
    if not await is_subscribed(user_id):
        await callback_query.message.answer(
            "Пожалуйста, подпишитесь на канал:", reply_markup=subscribe_keyboard()
        )
        return
    if not is_topup_enabled():
        await callback_query.message.answer("Пополнения временно остановлены.")
        await callback_query.answer()
        return
    ensure_user(user_id)
    await callback_query.answer()
    await callback_query.message.answer("Введите сумму пополнения баланса (в $):")
    await state.set_state(TopupBalance.waiting_for_amount)


@router.message(F.text == "💰 Пополнить баланс")
async def topup_balance_start_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_banned(user_id):
        await message.answer("Вы забанены")
        return
    if not await is_subscribed(user_id):
        await message.answer(
            "Пожалуйста, подпишитесь на канал:", reply_markup=subscribe_keyboard()
        )
        return
    if not is_topup_enabled():
        await message.answer("Пополнения временно остановлены.")
        return
    ensure_user(user_id)
    await message.answer("Введите сумму пополнения баланса (в $):")
    await state.set_state(TopupBalance.waiting_for_amount)


@router.message(TopupBalance.waiting_for_amount)
async def process_amount_balance(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректную сумму:")
        return
    await state.update_data(amount=amount)
    await message.answer(
        "Пожалуйста, отправьте чек с суммой, на которую нужно пополнить баланс"
    )
    await state.set_state(TopupBalance.waiting_for_receipt)


@router.message(TopupBalance.waiting_for_receipt, content_types=types.ContentTypes.ANY)
async def process_receipt_balance(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    amount = data.get("amount", 0.0)

    receipt_id = None
    if message.photo:
        receipt_id = message.photo[-1].file_id
    elif message.document:
        receipt_id = message.document.file_id
    else:
        receipt_id = message.text or ""

    purchase_id = add_purchase(
        user_id,
        {
            "type": "balance",
            "amount": amount,
            "receipt": receipt_id,
            "status": "pending",
        },
    )

    text = (
        f"Пользователь: {user_id}\n"
        f"Сумма: {amount} $" + ("" if message.photo or message.document else f"\nСсылка на чек: {receipt_id}")
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("В обработке", callback_data=f"processing_{purchase_id}"),
        InlineKeyboardButton("Отменить обработку", callback_data=f"cancel_{purchase_id}"),
    )
    if message.photo:
        await bot.send_photo(ADMIN_ID, receipt_id, caption=text, reply_markup=kb)
    elif message.document:
        await bot.send_document(ADMIN_ID, receipt_id, caption=text, reply_markup=kb)
    else:
        await bot.send_message(ADMIN_ID, text, reply_markup=kb)

    await message.answer("Запрос отправлен администратору", reply_markup=back_keyboard())
    await state.clear()


@router.callback_query(F.data.startswith("processing_"))
async def admin_processing(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 1)[1])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "processing")
    if purchase.get("type") == "balance":
        await bot.send_message(
            purchase["user_id"],
            f"Ваш запрос на пополнение баланса {purchase['amount']} $ принят в обработку",
        )
    else:
        await bot.send_message(
            purchase["user_id"],
            f"Ваш номер {purchase.get('phone')} принят в обработку",
        )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Оплачено", callback_data=f"paid_{purchase_id}"),
        InlineKeyboardButton("Отмена", callback_data=f"final_cancel_{purchase_id}"),
    )
    await callback_query.message.edit_reply_markup(kb)
    await callback_query.answer()


@router.callback_query(F.data.startswith("cancel_"))
async def admin_cancel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 1)[1])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "canceled")
    if purchase.get("type") == "balance":
        await bot.send_message(
            purchase["user_id"],
            f"Ваш запрос на пополнение баланса {purchase['amount']} $ отменён",
        )
    else:
        await bot.send_message(
            purchase["user_id"],
            f"Заявка на пополнение номера {purchase.get('phone')} отменена",
        )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Оплачено", callback_data=f"paid_{purchase_id}"),
        InlineKeyboardButton("Отмена", callback_data=f"final_cancel_{purchase_id}"),
    )
    await callback_query.message.edit_reply_markup(kb)
    await callback_query.answer()


@router.callback_query(F.data.startswith("paid_"))
async def admin_paid(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 1)[1])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "completed")
    if purchase.get("type") == "balance":
        add_balance(purchase["user_id"], purchase.get("amount", 0))
        await bot.send_message(
            purchase["user_id"],
            f"Баланс пополнен на {purchase.get('amount', 0)} $",
        )
    else:
        await bot.send_message(
            purchase["user_id"],
            f"Ваш номер {purchase.get('phone')} пополнен",
        )
    await callback_query.message.edit_text("Оплачено")
    await callback_query.answer()


@router.callback_query(F.data.startswith("final_cancel_"))
async def admin_final_cancel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Нет доступа", show_alert=True)
        return
    purchase_id = int(callback_query.data.split("_", 1)[1])
    purchase = get_purchase_by_id(purchase_id)
    if not purchase:
        await callback_query.answer("Не найдено", show_alert=True)
        return
    update_purchase_status(purchase["user_id"], purchase_id, "canceled")
    await bot.send_message(purchase["user_id"], "Заявка отменена")
    await callback_query.message.edit_text("Отменено")
    await callback_query.answer()
