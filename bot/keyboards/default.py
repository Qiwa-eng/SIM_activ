from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    """Create main reply keyboard with top level sections."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Объявления"))
    keyboard.add(KeyboardButton("Мой профиль"))
    keyboard.add(KeyboardButton("Репутация"))
    keyboard.add(KeyboardButton("Помощь"))
    return keyboard


def ads_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Объявления" section."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📌 Разместить объявление"))
    keyboard.add(KeyboardButton("🔍 Все объявления"))
    keyboard.add(KeyboardButton("🔔 Мои объявления"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard


def profile_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Мой профиль" section."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⭐ Репутация"))
    keyboard.add(KeyboardButton("👤 Моя статистика"))
    keyboard.add(KeyboardButton("⚙️ Настройки профиля"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard


def reputation_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Репутация" section."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("✅ Оставить отзыв"))
    keyboard.add(KeyboardButton("📊 Топ пользователей"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard


def help_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for the "Помощь" section."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📖 Правила площадки"))
    keyboard.add(KeyboardButton("❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ"))
    keyboard.add(KeyboardButton("👨‍💻 Поддержка"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard
