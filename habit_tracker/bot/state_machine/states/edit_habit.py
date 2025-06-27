from __future__ import annotations

import logging

from aiogram.types import CallbackQuery

from bot.states import HabitStates
from core import localizator

from bot.state_machine.states_factory import register_state
from data.schemas import HabitUpdate
from .abstract_habit import AbstractHabitState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache
    from bot.state_machine.istate import IState
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.edit_habit)
class EditHabitState(AbstractHabitState):
    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 habit_id: int,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._habit_id = habit_id
        self._habit: HabitUpdate | None = None

    async def on_enter(self) -> None:
        self._habit = await self.__retrieve_habit()
        await super().on_enter()

    async def _handle_submit(self, callback_query: CallbackQuery):
        l = localizator.localizator.lang(self._user_cache.language)
        await self.__update_habit()
        await callback_query.answer(l.habit_edit_updated)

    def _get_submit_button_text(self):
        return localizator.localizator.lang(self._user_cache.language).habit_edit_button_submit

    def _get_message_header(self) -> str:
        return f"{localizator.localizator.lang(self._user_cache.language).habit_edit_header}: {self._habit.name}\n"

    async def _handle_name(self, habit_name: str) -> str:
        if habit_name == self._habit.name:
            return habit_name
        return await super()._handle_name(habit_name)

    async def __update_habit(self):
        await self._backend_repository.update_habit(self._habit)

    async def __retrieve_habit(self) -> HabitUpdate:
        return await self._backend_repository.get_habit_by_user_id_and_id(self._user_cache.backend_id, self._habit_id)
