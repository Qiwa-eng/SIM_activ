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
    builder.button(text="📌 Выставить объявление", callback_data="post_ad")
    builder.button(text="📰 Объявления", callback_data="ads")
    builder.button(text="👤 Мой профиль", callback_data="profile")
    builder.button(text="⭐ Репутация", callback_data="reputation")
    builder.button(text="ℹ️ Помощь", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()


def ads_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the "Объявления" section."""

    builder = InlineKeyboardBuilder()
    builder.button(text="📰 Все объявления", callback_data="all_ads")
    builder.button(text="🔎 Поиск объявлений", callback_data="search_ads")
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
    builder.button(text="❓ FAQ", callback_data="faq")
    builder.button(text="👨‍💻 Поддержка", callback_data="support")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def ads_list_keyboard(ads: list[dict]) -> InlineKeyboardMarkup:
    """Build keyboard with buttons for each advertisement."""

    builder = InlineKeyboardBuilder()
    for ad in ads:
        builder.button(text=ad["title"], callback_data=f"view_ad:{ad['id']}")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def ad_view_keyboard(ad: dict, viewer_id: int) -> InlineKeyboardMarkup:
    """Keyboard for a single advertisement with contact and edit options."""

    builder = InlineKeyboardBuilder()
    url = (
        f"https://t.me/{ad['user_name']}" if ad.get("user_name") else f"tg://user?id={ad['user_id']}"
    )
    builder.button(text="📞 Связь", url=url)
    if ad["user_id"] == viewer_id:
        builder.button(text="✏️ Изменить", callback_data=f"edit_ad:{ad['id']}")
    builder.adjust(1)
    return builder.as_markup()


def ad_settings_keyboard(ad: dict) -> InlineKeyboardMarkup:
    """Keyboard for ad creation/editing settings."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text=("Изменить название" if ad.get("title") else "Добавить название"),
        callback_data="ad_set:title",
    )
    builder.button(
        text=("Изменить описание" if ad.get("text") else "Добавить описание"),
        callback_data="ad_set:text",
    )
    builder.button(
        text=("Изменить фото/гиф" if ad.get("photo") else "Добавить фото/гиф"),
        callback_data="ad_set:photo",
    )
    builder.button(
        text=("Изменить теги" if ad.get("tags") else "Добавить теги"),
        callback_data="ad_set:tags",
    )
    show_name = ad.get("show_name", True)
    builder.button(
        text=f"Показывать юзернейм: {'Да' if show_name else 'Нет'}",
        callback_data="ad_toggle_name",
    )
    builder.button(text="✅ Опубликовать", callback_data="ad_publish")
    builder.button(text="❌ Отмена", callback_data="ad_cancel")
    builder.adjust(1)
    return builder.as_markup()
