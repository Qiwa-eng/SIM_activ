from aiogram import Dispatcher

from .menu import router as menu_router
from .start import router as start_router


def register_handlers(dp: Dispatcher) -> None:
    """Include all routers to the dispatcher."""
    dp.include_router(start_router)
    dp.include_router(menu_router)
