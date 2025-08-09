from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from bot.states import HabitStates
import bot
from bot.menu import setup_menu

from bot.state_machine.states_interfaces import IState
from bot.state_machine.states_factory import register_state
from data.schemas.user import LanguageEnum

logger = logging.getLogger(__name__)


@register_state(HabitStates.init)
class InitState(IState):

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
            return self._create(HabitStates.registration)  #, user_id=user_id, user_name=user_name)

        self._user_cache.backend_id = user.id
        self._user_cache.language = user.language
        self._user_cache.timezone = user.timezone
        self._user_cache.is_inited = True

        print("id", user.id)
        print("language", user.language)
        print("timezone", user.timezone)

        return self._create(HabitStates.help_command)

    @staticmethod
    def __get_user_id(message: Message | CallbackQuery) -> int:
        if isinstance(message, Message):
            return message.chat.id
        elif isinstance(message, CallbackQuery):
            return message.message.chat.id

    @staticmethod
    def __get_user_name(message: Message | CallbackQuery) -> str:
        if isinstance(message, Message):
            return message.from_user.username
        elif isinstance(message, CallbackQuery):
            return message.from_user.username

    async def on_exit(self) -> None:
        await super().on_exit()
        language = self._user_cache.language or LanguageEnum.en
        await setup_menu(language, bot.bot_instance)
