"""Handlers for bot menu and actions."""

from typing import Any, Dict, Set

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    ad_settings_keyboard,
    ad_view_keyboard,
    ads_keyboard,
    ads_list_keyboard,
    help_keyboard,
    main_keyboard,
    profile_keyboard,
    reputation_keyboard,
)
from bot.services.db import (
    add_ad,
    add_review,
    get_ad,
    get_ads,
    get_top_users,
    get_user_ads,
    get_user_reputation,
    search_ads,
    update_ad,
)


router = Router()

# Simple in-memory state holders
_pending_ads: Dict[int, Dict[str, Any]] = {}
_pending_edit: Dict[int, Dict[str, Any]] = {}
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


def _ad_preview(ad: Dict[str, Any]) -> str:
    parts = []
    if ad.get("title"):
        parts.append(f"<b>{ad['title']}</b>")
    if ad.get("text"):
        parts.append(ad["text"])
    if ad.get("tags"):
        parts.append("Теги: " + " ".join(f"#{t}" for t in ad["tags"]))
    if not parts:
        parts.append("Пока пусто")
    return "Ваше объявление выглядит так:\n\n" + "\n".join(parts)


async def _show_ad_preview(message: Message, ad: Dict[str, Any]) -> None:
    text = _ad_preview(ad)
    if ad.get("photo"):
        await message.answer_photo(
            ad["photo"], caption=text, reply_markup=ad_settings_keyboard(ad), parse_mode="HTML"
        )
    else:
        await message.answer(text, reply_markup=ad_settings_keyboard(ad), parse_mode="HTML")


@router.callback_query(F.data == "post_ad")
async def post_ad(callback: CallbackQuery) -> None:
    _pending_ads[callback.from_user.id] = {
        "ad": {"title": None, "text": None, "photo": None, "tags": [], "show_name": True},
        "step": None,
    }
    await _show_ad_preview(callback.message, _pending_ads[callback.from_user.id]["ad"])
    await callback.answer()


@router.callback_query(F.data.startswith("ad_set:"))
async def ad_set_field(callback: CallbackQuery) -> None:
    data = _pending_ads.get(callback.from_user.id)
    if not data:
        await callback.answer("Сначала начните создание", show_alert=True)
        return
    field = callback.data.split(":")[1]
    data["step"] = field
    prompts = {
        "title": "📌 Введите название объявления",
        "text": "📝 Введите описание объявления",
        "photo": "📷 Пришлите фото или гиф",
        "tags": "🏷️ Укажите теги через запятую",
    }
    await callback.message.answer(prompts[field])
    await callback.answer()


@router.message(
    lambda m: m.from_user.id in _pending_ads and _pending_ads[m.from_user.id]["step"]
)
async def ad_field_input(message: Message) -> None:
    data = _pending_ads[message.from_user.id]
    field = data["step"]
    ad = data["ad"]
    if field == "title":
        ad["title"] = message.text
    elif field == "text":
        ad["text"] = message.text
    elif field == "photo":
        if message.photo:
            ad["photo"] = message.photo[-1].file_id
        elif message.animation:
            ad["photo"] = message.animation.file_id
        else:
            await message.answer("Пришлите фото или гиф")
            return
    elif field == "tags":
        ad["tags"] = [t.strip() for t in message.text.split(",") if t.strip()]
    data["step"] = None
    await _show_ad_preview(message, ad)


@router.callback_query(F.data == "ad_toggle_name")
async def ad_toggle_name(callback: CallbackQuery) -> None:
    data = _pending_ads.get(callback.from_user.id)
    if not data:
        await callback.answer("Нет объявления", show_alert=True)
        return
    ad = data["ad"]
    ad["show_name"] = not ad.get("show_name", True)
    await _show_ad_preview(callback.message, ad)
    await callback.answer()


@router.callback_query(F.data == "ad_publish")
async def ad_publish(callback: CallbackQuery) -> None:
    data = _pending_ads.get(callback.from_user.id)
    if not data:
        await callback.answer("Нет объявления", show_alert=True)
        return
    ad = data["ad"]
    if not ad.get("title") or not ad.get("text"):
        await callback.answer("Добавьте название и описание", show_alert=True)
        return
    user_name = callback.from_user.username if ad.get("show_name") else None
    add_ad(
        user_id=callback.from_user.id,
        title=ad["title"],
        text=ad["text"],
        tags=ad.get("tags", []),
        photo=ad.get("photo"),
        user_name=user_name,
    )
    del _pending_ads[callback.from_user.id]
    await callback.message.answer("✅ Объявление сохранено!")
    await callback.answer()


@router.callback_query(F.data == "ad_cancel")
async def ad_cancel(callback: CallbackQuery) -> None:
    _pending_ads.pop(callback.from_user.id, None)
    await callback.message.answer("❌ Создание объявления отменено")
    await callback.answer()


@router.callback_query(F.data == "all_ads")
async def all_ads(callback: CallbackQuery) -> None:
    ads = get_ads()
    if not ads:
        await callback.message.answer("Пока нет объявлений.")
    else:
        await callback.message.answer(
            "Все объявления:", reply_markup=ads_list_keyboard(ads)
        )
    await callback.answer()


@router.callback_query(F.data == "my_ads")
async def my_ads(callback: CallbackQuery) -> None:
    ads = get_user_ads(callback.from_user.id)
    if not ads:
        await callback.message.answer("У вас нет объявлений.")
    else:
        await callback.message.answer(
            "Ваши объявления:", reply_markup=ads_list_keyboard(ads)
        )
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
    await message.answer(
        "Результаты поиска:", reply_markup=ads_list_keyboard(results)
    )


@router.callback_query(F.data.startswith("view_ad:"))
async def view_ad(callback: CallbackQuery) -> None:
    ad_id = int(callback.data.split(":")[1])
    ad = get_ad(ad_id)
    if not ad:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    text = f"<b>{ad['title']}</b>\n{ad['text']}"
    if ad["tags"]:
        text += "\nТеги: " + " ".join(f"#{t}" for t in ad["tags"])
    markup = ad_view_keyboard(ad, callback.from_user.id)
    if ad.get("photo"):
        await callback.message.answer_photo(ad["photo"], caption=text, reply_markup=markup)
    else:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_ad:"))
async def edit_ad_start(callback: CallbackQuery) -> None:
    ad_id = int(callback.data.split(":")[1])
    ad = get_ad(ad_id)
    if not ad or ad["user_id"] != callback.from_user.id:
        await callback.answer("Нельзя редактировать", show_alert=True)
        return
    _pending_edit[callback.from_user.id] = {"id": ad_id, "step": "title", "ad": ad}
    await callback.message.answer("Введите новое название (или /skip)")
    await callback.answer()


@router.message(lambda m: m.from_user.id in _pending_edit)
async def edit_ad_process(message: Message) -> None:
    data = _pending_edit[message.from_user.id]
    step = data["step"]
    ad = data["ad"]
    if step == "title":
        if message.text != "/skip":
            ad["title"] = message.text
        data["step"] = "text"
        await message.answer("Введите новый текст (или /skip)")
    elif step == "text":
        if message.text != "/skip":
            ad["text"] = message.text
        data["step"] = "photo"
        await message.answer("Пришлите новое фото или отправьте /skip")
    elif step == "photo":
        if message.photo:
            ad["photo"] = message.photo[-1].file_id
        elif message.text != "/skip":
            await message.answer("Пришлите фото или /skip")
            return
        data["step"] = "tags"
        await message.answer("Укажите теги через запятую (или /skip)")
    elif step == "tags":
        if message.text != "/skip":
            ad["tags"] = [t.strip() for t in message.text.split(",") if t.strip()]
        update_ad(data["id"], ad)
        del _pending_edit[message.from_user.id]
        await message.answer("✅ Объявление обновлено!")


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

