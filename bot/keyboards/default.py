"""Inline keyboards used across the bot.

Previously this module constructed ReplyKeyboardMarkup and sent them as
persistent reply keyboards. To make buttons attached to messages we now
use inline keyboards built with InlineKeyboardBuilder.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard() -> InlineKeyboardMarkup:
    """Create main menu inline keyboard."""

    builder = InlineKeyboardBuilder()
    builder.button(text="Объявления", callback_data="ads")
    builder.button(text="Мой профиль", callback_data="profile")
    builder.button(text="Репутация", callback_data="reputation")
    builder.button(text="Помощь", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()


def ads_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the "Объявления" section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Разместить объявление", callback_data="post_ad")
    builder.button(text="🔍 Все объявления", callback_data="all_ads")
    builder.button(text="🔔 Мои объявления", callback_data="my_ads")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the "Мой профиль" section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Репутация", callback_data="rep")
    builder.button(text="👤 Моя статистика", callback_data="stats")
    builder.button(text="⚙️ Настройки профиля", callback_data="settings")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def reputation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the "Репутация" section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оставить отзыв", callback_data="leave_review")
    builder.button(text="📊 Топ пользователей", callback_data="top_users")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def help_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the "Помощь" section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Правила площадки", callback_data="rules")
    builder.button(text="❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ", callback_data="faq")
    builder.button(text="👨‍💻 Поддержка", callback_data="support")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()
