"""Reply keyboards used across the bot.

This module previously relied on :class:`aiogram.types.ReplyKeyboardMarkup`
to construct keyboards using the ``add`` method just like in aiogram v2.
With aiogram v3 the ``ReplyKeyboardMarkup`` model is based on Pydantic and
requires the ``keyboard`` field on creation. The old approach resulted in
``ValidationError: Field required`` because we instantiated the markup
without buttons and tried to add them afterwards.

The fix is to utilise :class:`aiogram.utils.keyboard.ReplyKeyboardBuilder`
which provides a convenient API for building keyboards and returns a
properly initialised :class:`ReplyKeyboardMarkup` instance.
"""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_keyboard() -> ReplyKeyboardMarkup:
    """Create main reply keyboard with top level sections."""

    builder = ReplyKeyboardBuilder()
    builder.button(text="Объявления")
    builder.button(text="Мой профиль")
    builder.button(text="Репутация")
    builder.button(text="Помощь")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def ads_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Объявления" section."""

    builder = ReplyKeyboardBuilder()
    builder.button(text="📌 Разместить объявление")
    builder.button(text="🔍 Все объявления")
    builder.button(text="🔔 Мои объявления")
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def profile_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Мой профиль" section."""

    builder = ReplyKeyboardBuilder()
    builder.button(text="⭐ Репутация")
    builder.button(text="👤 Моя статистика")
    builder.button(text="⚙️ Настройки профиля")
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def reputation_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Репутация" section."""

    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Оставить отзыв")
    builder.button(text="📊 Топ пользователей")
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def help_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Помощь" section."""

    builder = ReplyKeyboardBuilder()
    builder.button(text="📖 Правила площадки")
    builder.button(text="❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ")
    builder.button(text="👨‍💻 Поддержка")
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
