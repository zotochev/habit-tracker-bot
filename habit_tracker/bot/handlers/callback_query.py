from aiogram import Router
from aiogram.types import (
    CallbackQuery,
)

from bot.cache import UserCache


router = Router()


@router.callback_query()
async def universal(callback_query: CallbackQuery, user_cache: UserCache):
    await user_cache.state_machine.handle(callback_query)
