from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core import localizator

from bot.states import HabitStates
from bot.state_machine.states_factory import register_state
from bot.state_machine.states_interfaces import IState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository
    from data.schemas import HabitUpdate

logger = logging.getLogger(__name__)


@register_state(HabitStates.delete_habit)
class DeleteState(IState):
    YES_CDATA = 'yes'
    NO_CDATA = 'no'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 habit_id: int,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._habit_id = habit_id
        self._habit: HabitUpdate | None = None

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        match callback_query.data:
            case self.YES_CDATA:
                await self._backend_repository.delete_habit(self._user_cache.backend_id, self._habit_id)
                return self._create(HabitStates.end)
            case self.NO_CDATA:
                return self._create(HabitStates.end)

        return await self._handle()

    async def _handle(self):
        return self

    async def on_enter(self) -> None:
        await super().on_enter()

        self._habit = await self.__retrieve_habit()

        text = self.__get_message_text()
        keyboard = self.__get_message_keyboard()

        await self._user_cache.messanger.update_main_message(text, keyboard)

    async def __retrieve_habit(self) -> HabitUpdate:
        return await self._backend_repository.get_habit_by_user_id_and_id(self._user_cache.backend_id, self._habit_id)

    def __get_message_text(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)
        return f'{l.delete_are_you_sure_button}: {self._habit.name}'

    def __get_message_keyboard(self) -> InlineKeyboardMarkup:
        l = localizator.localizator.lang(self._user_cache.language)

        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=l.yes_button,
                    callback_data=self.YES_CDATA,
                ),
                InlineKeyboardButton(
                    text=l.no_button,
                    callback_data=self.NO_CDATA,
                ),
            ]
        ])
