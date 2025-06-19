from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from bot import cache


class UserStateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, CallbackQuery):
            data["user_cache"] = cache.cache.user(event.from_user.id)
        elif isinstance(event, Message):
            data["user_cache"] = cache.cache.user(event.chat.id)
        return await handler(event, data)
