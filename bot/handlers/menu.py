from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards import (
    ads_keyboard,
    help_keyboard,
    main_keyboard,
    profile_keyboard,
    reputation_keyboard,
)

router = Router()


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


@router.callback_query(
    F.data.in_(
        {
            "post_ad",
            "all_ads",
            "my_ads",
            "rep",
            "stats",
            "settings",
            "leave_review",
            "top_users",
            "rules",
            "faq",
            "support",
        }
    )
)
async def menu_stub(callback: CallbackQuery) -> None:
    await callback.answer("Эта функция пока не реализована.")
