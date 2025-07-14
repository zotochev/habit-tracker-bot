from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from bot import cache
from bot.states import HabitStates
from data.factory import get_backend_repository
from data.schemas import User


class UserStateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_cache = None

        if isinstance(event, CallbackQuery):
            user_cache = cache.cache.user(event.message.chat.id)
            user_cache.last_datetime = event.message.date

        elif isinstance(event, Message):
            user_cache = cache.cache.user(event.chat.id)
            user_cache.last_datetime = event.date
            user_cache.messanger.register_recv_message(event.message_id)

        if user_cache is not None:
            if not user_cache.is_registered():
                await user_cache.state_machine.set_state(HabitStates.registration)

            data["user_cache"] = user_cache

        return await handler(event, data)

    @staticmethod
    async def __retrieve_user_data(telegram_id: int, user_name: str) -> User:
        repository = get_backend_repository()

        return await repository.get_user_info(telegram_id)
