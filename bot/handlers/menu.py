"""Handlers for bot menu and actions."""

from typing import Set

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    ads_keyboard,
    help_keyboard,
    main_keyboard,
    profile_keyboard,
    reputation_keyboard,
)
from bot.services.db import (
    add_ad,
    add_review,
    get_ads,
    get_top_users,
    get_user_ads,
    get_user_reputation,
    search_ads,
)


router = Router()

# Simple in-memory state holders
_pending_ads: Set[int] = set()
_pending_search: Set[int] = set()
_pending_review: Set[int] = set()


@router.callback_query(F.data == "ads")
async def menu_ads(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Раздел: объявления", reply_markup=ads_keyboard())
    await callback.answer()


@router.callback_query(F.data == "profile")
async def menu_profile(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Раздел: мой профиль", reply_markup=profile_keyboard())
    await callback.answer()


@router.callback_query(F.data == "reputation")
async def menu_reputation(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Раздел: репутация", reply_markup=reputation_keyboard())
    await callback.answer()


@router.callback_query(F.data == "help")
async def menu_help(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Раздел: помощь", reply_markup=help_keyboard())
    await callback.answer()


@router.callback_query(F.data == "back")
async def menu_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Главное меню", reply_markup=main_keyboard())
    await callback.answer()


# --- Advertisements -------------------------------------------------------


@router.callback_query(F.data == "post_ad")
async def post_ad(callback: CallbackQuery) -> None:
    _pending_ads.add(callback.from_user.id)
    await callback.message.answer("📝 Пришлите текст объявления")
    await callback.answer()


@router.message(lambda m: m.from_user.id in _pending_ads)
async def save_ad(message: Message) -> None:
    add_ad(message.from_user.id, message.text)
    _pending_ads.discard(message.from_user.id)
    await message.answer("✅ Объявление сохранено!")


@router.callback_query(F.data == "all_ads")
async def all_ads(callback: CallbackQuery) -> None:
    ads = get_ads()
    if not ads:
        text = "Пока нет объявлений."
    else:
        text = "\n\n".join(
            f"{ad['id']}. {ad['text']} (от {ad['user_id']})" for ad in ads
        )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "my_ads")
async def my_ads(callback: CallbackQuery) -> None:
    ads = get_user_ads(callback.from_user.id)
    if not ads:
        text = "У вас нет объявлений."
    else:
        text = "\n\n".join(f"{ad['id']}. {ad['text']}" for ad in ads)
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "search_ads")
async def search_start(callback: CallbackQuery) -> None:
    _pending_search.add(callback.from_user.id)
    await callback.message.answer("🔎 Введите ключевое слово для поиска")
    await callback.answer()


@router.message(lambda m: m.from_user.id in _pending_search)
async def search_finish(message: Message) -> None:
    results = search_ads(message.text)
    _pending_search.discard(message.from_user.id)
    if not results:
        await message.answer("Ничего не найдено")
        return
    text = "\n\n".join(
        f"{ad['id']}. {ad['text']} (от {ad['user_id']})" for ad in results
    )
    await message.answer(text)


# --- Profile --------------------------------------------------------------


@router.callback_query(F.data == "rep")
async def profile_rep(callback: CallbackQuery) -> None:
    rep = get_user_reputation(callback.from_user.id)
    await callback.message.answer(f"Ваша репутация: {rep} 👍")
    await callback.answer()


@router.callback_query(F.data == "stats")
async def profile_stats(callback: CallbackQuery) -> None:
    ads = get_user_ads(callback.from_user.id)
    await callback.message.answer(f"Вы разместили {len(ads)} объявлений")
    await callback.answer()


@router.callback_query(F.data == "settings")
async def profile_settings(callback: CallbackQuery) -> None:
    await callback.message.answer("Настройки пока недоступны")
    await callback.answer()


# --- Reputation -----------------------------------------------------------


@router.callback_query(F.data == "leave_review")
async def review_start(callback: CallbackQuery) -> None:
    _pending_review.add(callback.from_user.id)
    await callback.message.answer(
        "Введите ID пользователя и отзыв через пробел: \n" "`123 Спасибо!`"
    )
    await callback.answer()


@router.message(lambda m: m.from_user.id in _pending_review)
async def review_finish(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[0].isdigit():
        await message.answer("Неверный формат. Пример: 123 Спасибо!")
        return
    to_user = int(parts[0])
    add_review(message.from_user.id, to_user, parts[1])
    _pending_review.discard(message.from_user.id)
    await message.answer("🙏 Спасибо за отзыв!")


@router.callback_query(F.data == "top_users")
async def reputation_top(callback: CallbackQuery) -> None:
    top = get_top_users()
    if not top:
        text = "Отзывов пока нет"
    else:
        text = "Топ пользователей:\n" + "\n".join(
            f"{user_id}: {score}" for user_id, score in top
        )
    await callback.message.answer(text)
    await callback.answer()


# --- Help -----------------------------------------------------------------


@router.callback_query(F.data == "rules")
async def help_rules(callback: CallbackQuery) -> None:
    await callback.message.answer("1. Будьте вежливы\n2. Не спамьте")
    await callback.answer()


@router.callback_query(F.data == "faq")
async def help_faq(callback: CallbackQuery) -> None:
    await callback.message.answer("Частые вопросы пока отсутствуют")
    await callback.answer()


@router.callback_query(F.data == "support")
async def help_support(callback: CallbackQuery) -> None:
    await callback.message.answer("Пишите в поддержку: @support")
    await callback.answer()

