from __future__ import annotations

import inspect
import datetime
from enum import StrEnum, auto
import logging

from pydantic import ValidationError
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import dateparser

from bot.states import HabitStates
import bot
from core import localizator
from data.schemas import HabitBuffer

from bot.state_machine.istate import IState
from bot.state_machine.isuspendable_state import ISuspendableState
from bot.state_machine.states_factory import register_state

from .abstract_habit import AbstractHabitState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


class HabitField(StrEnum):
    name = auto()
    description = auto()
    times_per_day = auto()
    start_date = auto()
    end_date = auto()


HABIT_BUTTON_SUBMIT = 'habit_button_submit'


class FieldHandleError(Exception):
    pass


@register_state(HabitStates.add_habit)
class AddHabitState(AbstractHabitState):
    async def _handle_submit(self, callback_query: CallbackQuery):
        l = localizator.localizator.lang(self._user_cache.language)
        await self._backend_repository.create_habit(self._user_cache.backend_id, self._habit)
        await callback_query.answer(l.habit_created)

    def _get_message_header(self) -> str:
        return f"{localizator.localizator.lang(self._user_cache.language).habit_header}\n"
