from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.menu import setup_menu

from bot.state_machine.istate import IState
from bot.state_machine.states_factory import register_state

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


@register_state(HabitStates.init)
class InitState(IState):
    # state = HabitStates.init

    async def _handle_message(self, message: Message) -> IState:
        user_id = self.__get_user_id(message)
        user_name = self.__get_user_name(message)
        return await self._handle(user_id, user_name)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        user_id = self.__get_user_id(callback_query)
        user_name = self.__get_user_name(callback_query)
        await callback_query.answer()
        return await self._handle(user_id, user_name)

    async def _handle(self, user_id: int, user_name: str) -> IState:
        # retrieve data from backend
        user = await self._backend_repository.get_user_info(user_id)

        # if there is no data on backend register user and ask for language
        if user is None:
            telegram_account = await self._backend_repository.register_user_by_telegram(
                user_name=user_name,
                telegram_id=user_id,
            )
            assert telegram_account, f"Failed to register user: {user_id}:{user_name}"
            self._user_cache.backend_id = telegram_account.user_id
            return self._create(HabitStates.choose_language)

        self._user_cache.backend_id = user.id
        self._user_cache.language = user.language

        if user.language is None:
            return self._create(HabitStates.choose_language)

        return self._create(HabitStates.wait_command)

    @staticmethod
    def __get_user_id(message: Message | CallbackQuery) -> int:
        if isinstance(message, Message):
            return message.from_user.id
        elif isinstance(message, CallbackQuery):
            return message.from_user.id

    @staticmethod
    def __get_user_name(message: Message | CallbackQuery) -> str:
        if isinstance(message, Message):
            return message.from_user.username
        elif isinstance(message, CallbackQuery):
            return message.from_user.username

    async def on_exit(self) -> None:
        await super().on_exit()
        await setup_menu(self._user_cache.language, bot.bot_instance)
