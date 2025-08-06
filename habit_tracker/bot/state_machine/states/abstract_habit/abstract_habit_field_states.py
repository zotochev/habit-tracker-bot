from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
import logging
import datetime

import dateparser

from core import localizator
from data.schemas import HabitBuffer, HabitRepeatType

from .habit_field_enum import HabitField
from .exceptions import FieldHandleError

from typing import TYPE_CHECKING, Literal, Union
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__file__)


class FieldStateInputType(Enum):
    message = auto()
    callback_query = auto()


class IFieldState(ABC):
    field: HabitField

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            backend_repository: BackendRepository,
            user_cache: UserCache,
    ) -> None:
        self._habit_buffer = habit_buffer
        self._backend_repository = backend_repository
        self._user_cache = user_cache

    @abstractmethod
    async def handle(self, text: str) -> IFieldState:
        ...

    @abstractmethod
    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        ...


class NameFieldState(IFieldState):
    field = HabitField.name

    async def handle(self, text: str) -> IFieldState:
        habit_name = text
        habit = await self._backend_repository.get_habit_by_user_id_and_name(self._user_cache.backend_id, habit_name)
        if habit is not None:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_name_already_in_use)
        self._habit_buffer.name = habit_name
        return DescriptionFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)


class DescriptionFieldState(IFieldState):
    field = HabitField.description

    async def handle(self, text: str) -> IFieldState:
        self._habit_buffer.description = text
        return TimesPerDayFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)


class TimesPerDayFieldState(IFieldState):
    field = HabitField.times_per_day

    async def handle(self, text: str) -> IFieldState:
        try:
            self._habit_buffer.times_per_day = int(text)
        except Exception:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_times)
        return StartDateFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)


class DateFieldState(IFieldState):
    async def handle(self, text: str) -> IFieldState:
        try:
            self._set_field(dateparser.parse(text).date())
        except Exception:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_date)
        return self._next_state(self._habit_buffer, self._backend_repository, self._user_cache)

    @abstractmethod
    def _set_field(self, field_date: datetime.date) -> None:
        ...

    @property
    @abstractmethod
    def _next_state(self) -> type[IFieldState]:
        ...

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)


class StartDateFieldState(DateFieldState):
    field = HabitField.start_date

    def _set_field(self, field_date: datetime.date) -> None:
        self._habit_buffer.start_date = field_date

    @property
    def _next_state(self) -> type[IFieldState]:
        return EndDateFieldState


class EndDateFieldState(DateFieldState):
    field = HabitField.end_date

    @property
    def _next_state(self) -> type[IFieldState]:
        return RepeatTypeFieldState

    def _set_field(self, field_date: datetime.date) -> None:
        self._habit_buffer.end_date = field_date


class RepeatTypeFieldState(IFieldState):
    field = HabitField.repeat_type

    async def handle(self, text: str) -> IFieldState:
        l = localizator.localizator.lang(self._user_cache.language)
        try:
            self._habit_buffer.repeat_type = HabitRepeatType(int(text))
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.__handle_repeat_type({text}) -> {e.__class__.__name__}: {e}")
            raise FieldHandleError(l.habit_repeat_invalid_input)
        return NameFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.callback_query,)


field_states_factory = {
    s.field: s
    for s in (
        NameFieldState,
        DescriptionFieldState,
        TimesPerDayFieldState,
        StartDateFieldState,
        EndDateFieldState,
        RepeatTypeFieldState,
    )
}
