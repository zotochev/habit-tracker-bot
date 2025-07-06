from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from bot import cache
from data.factory import get_backend_repository
from data.schemas import User


class UserStateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_cache = None

        if isinstance(event, CallbackQuery):
            user_cache = cache.cache.user(event.from_user.id)
            user_cache.last_datetime = event.message.date

        elif isinstance(event, Message):
            user_cache = cache.cache.user(event.chat.id)
            user_cache.last_datetime = event.date
            user_cache.messanger.register_recv_message(event.message_id)

        if user_cache is not None:
            if user_cache.backend_id is None:
                user = await self.__retrieve_user_data(event.from_user.id, event.from_user.username)
                user_cache.backend_id = user.id
                user_cache.language = user.language
            data["user_cache"] = user_cache

        return await handler(event, data)

    @staticmethod
    async def __retrieve_user_data(telegram_id: int, user_name: str) -> User:
        repository = get_backend_repository()

        # retrieve data from backend
        user = await repository.get_user_info(telegram_id)

        # if there is no data on backend register user and ask for language
        if user is None:
            telegram_account = await repository.register_user_by_telegram(
                user_name=user_name,
                telegram_id=telegram_id,
            )
            assert telegram_account, f"Failed to register user: {telegram_id}:{user_name}"
            user = await repository.get_user_info(telegram_id)
        return user
