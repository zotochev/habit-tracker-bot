from __future__ import annotations
import logging
from functools import partial

from aiogram.types import Message, CallbackQuery

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from bot.state_machine.states_interfaces import IState, INoneSwitchable, ISuspendableState, IImmediateHandle

from core import localizator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.registration)
class RegistrationState(IState, ISuspendableState, INoneSwitchable, IImmediateHandle):
    DONE_ACTION = 'done'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 **kwargs,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory, **kwargs)
        self.__registration_flow = [
            self.DONE_ACTION,
            HabitStates.choose_timezone,
            HabitStates.choose_language,
        ]
        self.__registration_handlers = {
            HabitStates.choose_language: partial(self._create, HabitStates.choose_language),
            HabitStates.choose_timezone: partial(self._create, HabitStates.choose_timezone),
            self.DONE_ACTION: partial(self._create, HabitStates.end),
        }
        self.__user_id: int | None = None
        self.__user_name: str | None = None

    async def _handle_message(self, message: Message) -> IState:
        if self._user_cache.backend_id is None:
            self.__user_id = message.chat.id
            self.__user_name = message.chat.username
            await self.__register_user()

        return await self._handle(message.text)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        message_text = callback_query.data
        await callback_query.answer()
        return await self._handle(message_text)

    async def _handle(self, message_text: str) -> IState:
        assert self.__registration_flow, 'Unexpected that there are not actions to handle in registration flow'

        action = self.__registration_flow.pop()
        return self.__registration_handlers[action]()

    async def on_enter(self) -> None:
        await super().on_enter()

    async def __register_user(self):
        assert self.__user_id is not None and self.__user_name is not None

        telegram_account = await self._backend_repository.register_user_by_telegram(
            user_name=self.__user_name,
            telegram_id=self.__user_id,
        )
        assert telegram_account, f"Failed to register user: {self.__user_id}:{self.__user_name}"
        self._user_cache.backend_id = telegram_account.id
        return self
