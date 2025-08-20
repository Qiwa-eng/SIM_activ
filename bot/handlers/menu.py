from aiogram import Router, F
from aiogram.types import Message

from bot.keyboards import (
    ads_keyboard,
    help_keyboard,
    main_keyboard,
    profile_keyboard,
    reputation_keyboard,
)

router = Router()


@router.message(F.text == "Объявления")
async def menu_ads(message: Message) -> None:
    await message.answer("Раздел: объявления", reply_markup=ads_keyboard())


@router.message(F.text == "Мой профиль")
async def menu_profile(message: Message) -> None:
    await message.answer("Раздел: мой профиль", reply_markup=profile_keyboard())


@router.message(F.text == "Репутация")
async def menu_reputation(message: Message) -> None:
    await message.answer("Раздел: репутация", reply_markup=reputation_keyboard())


@router.message(F.text == "Помощь")
async def menu_help(message: Message) -> None:
    await message.answer("Раздел: помощь", reply_markup=help_keyboard())


@router.message(F.text == "⬅️ Назад")
async def menu_back(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=main_keyboard())


@router.message(
    F.text.in_(
        {
            "📌 Разместить объявление",
            "🔍 Все объявления",
            "🔔 Мои объявления",
            "⭐ Репутация",
            "👤 Моя статистика",
            "⚙️ Настройки профиля",
            "✅ Оставить отзыв",
            "📊 Топ пользователей",
            "📖 Правила площадки",
            "❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ",
            "👨‍💻 Поддержка",
        }
    )
)
async def menu_stub(message: Message) -> None:
    await message.answer("Эта функция пока не реализована.")
