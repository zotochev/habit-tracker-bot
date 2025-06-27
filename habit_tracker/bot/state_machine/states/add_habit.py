from __future__ import annotations

import logging

from aiogram.types import CallbackQuery

from bot.states import HabitStates
from core import localizator

from bot.state_machine.states_factory import register_state

from .abstract_habit import AbstractHabitState


logger = logging.getLogger(__name__)


@register_state(HabitStates.add_habit)
class AddHabitState(AbstractHabitState):
    async def _handle_submit(self, callback_query: CallbackQuery):
        l = localizator.localizator.lang(self._user_cache.language)
        await self._backend_repository.create_habit(self._user_cache.backend_id, self._habit)
        await callback_query.answer(l.habit_created)

    def _get_message_header(self) -> str:
        return f"{localizator.localizator.lang(self._user_cache.language).habit_header}\n"

    def _get_submit_button_text(self):
        l = localizator.localizator
        return l.lang(self._user_cache.language).habit_button_submit
