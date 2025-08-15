from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import CHANNEL_LINK

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

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )

def operators_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Т2", callback_data="op_T2"),
        InlineKeyboardButton("Мегафон", callback_data="op_Мегафон"),
        InlineKeyboardButton("МТС", callback_data="op_МТС"),
        InlineKeyboardButton("Билайн", callback_data="op_Билайн"),
        InlineKeyboardButton("Йота", callback_data="op_Йота"),
    )
    return kb


def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("🚫 Бан пользователя", callback_data="admin_ban"),
        InlineKeyboardButton("📦 Все покупки", callback_data="admin_purchases"),
        InlineKeyboardButton("👥 Все пользователи", callback_data="admin_users"),
        InlineKeyboardButton("⛔ Остановить пополнения", callback_data="admin_topups"),
    )
    return kb


def topup_control_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    if enabled:
        kb.add(InlineKeyboardButton("Остановить все", callback_data="topup_stop_all"))
    else:
        kb.add(InlineKeyboardButton("Возобновить все", callback_data="topup_enable_all"))
    kb.add(InlineKeyboardButton("Остановить/включить оператора", callback_data="topup_toggle_operator"))
    return kb
