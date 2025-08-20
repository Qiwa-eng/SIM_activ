from aiogram import Router
from aiogram.types import Message

from ..keyboards import main_keyboard

router = Router()


@router.message(commands=["start"])
async def cmd_start(message: Message) -> None:
    """Handle the /start command."""
    await message.answer(
        "Привет! Выберите нужный раздел:", reply_markup=main_keyboard()
    )
