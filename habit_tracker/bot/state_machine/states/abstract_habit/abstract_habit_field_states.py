from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
import logging
import datetime

import dateparser
from aiogram.types import InlineKeyboardButton

from core import localizator
from data.schemas import HabitBuffer, HabitRepeatType
from core.timezone_utils import utc_to_local, local_to_utc

from .habit_field_enum import HabitField
from .exceptions import FieldHandleError

from typing import TYPE_CHECKING, Literal, Union
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


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

    @staticmethod
    def keyboard() -> list[list[InlineKeyboardButton]] | None:
        return None


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

    TYPE_STATE = 0
    DAYS_STATE = 1

    SUBMIT_CALLBACK_DATA = 'REPEAT_TYPE_FIELD_STATE_SUBMIT'

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            backend_repository: BackendRepository,
            user_cache: UserCache,
    ) -> None:
        super().__init__(habit_buffer, backend_repository, user_cache)
        self.__state = self.TYPE_STATE

    async def handle(self, text: str) -> IFieldState:
        l = localizator.localizator.lang(self._user_cache.language)

        if text == self.SUBMIT_CALLBACK_DATA:
            return NotificationsFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

        try:
            match self.__state:
                case self.TYPE_STATE:
                    self._habit_buffer.repeat_type = HabitRepeatType(int(text))
                    self.__state = self.DAYS_STATE
                    if self._habit_buffer.repeat_type != HabitRepeatType.daily:
                        return self
                case self.DAYS_STATE:
                    dummy_day = datetime.datetime.fromisoformat(text)
                    if self._habit_buffer.is_day_set(dummy_day):
                        self._habit_buffer.unset_day(dummy_day)
                    else:
                        self._habit_buffer.set_day(dummy_day)
                    return self
                case _:
                    raise FieldHandleError(f"Unexpected Repeat Type state: {self.__state}")
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.handle({text}) -> {e.__class__.__name__}: {e}")
            raise FieldHandleError(l.habit_repeat_invalid_input)

        return NotificationsFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.callback_query,)

    def keyboard(self) -> list[list[InlineKeyboardButton]] | None:
        l = localizator.localizator.lang(self._user_cache.language)

        match self.__state:
            case self.TYPE_STATE:
                translations = {
                    HabitRepeatType.daily: l.habit_repeat_type_daily,
                    HabitRepeatType.weekly: l.habit_repeat_type_weekly,
                    HabitRepeatType.monthly: l.habit_repeat_type_monthly,
                }
                return [
                    [
                        InlineKeyboardButton(
                            text=translations[habit_repeat_type],
                            callback_data=str(habit_repeat_type.value),
                        ),
                    ] for habit_repeat_type in HabitRepeatType
                ]
            case self.DAYS_STATE:
                match self._habit_buffer.repeat_type:
                    case HabitRepeatType.daily:
                        raise FieldHandleError(f"Unexpected daily repeat type")
                    case HabitRepeatType.weekly:
                        keyboard = [[]]

                        for i, day_name in enumerate((l.monday_short,
                                                      l.tuesday_short,
                                                      l.wednesday_short,
                                                      l.thursday_short,
                                                      l.friday_short,
                                                      l.saturday_short,
                                                      l.sunday_short)):
                            dummy_day = datetime.date(1990, 4, 2) + datetime.timedelta(days=i)
                            is_checked = self._habit_buffer.is_day_set(dummy_day)

                            keyboard[0].append(
                                InlineKeyboardButton(
                                    text=f'{"✅" if is_checked else ""} {day_name}',
                                    callback_data=dummy_day.isoformat(),
                                )
                            )

                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    text=l.button_next,
                                    callback_data=self.SUBMIT_CALLBACK_DATA,
                                )
                            ]
                        )
                        return keyboard
                    case HabitRepeatType.monthly:
                        keyboard = [[] for _ in range(5)]  # 5 weeks in a month with 31 day

                        for i in range(31):
                            dummy_day = datetime.date(1990, 3, 1) + datetime.timedelta(days=i)
                            is_checked = self._habit_buffer.is_day_set(dummy_day)

                            keyboard[i // 7].append(
                                InlineKeyboardButton(
                                    text=f'{"✅" if is_checked else ""} {dummy_day.day}',
                                    callback_data=dummy_day.isoformat(),
                                )
                            )

                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    text=l.button_next,
                                    callback_data=self.SUBMIT_CALLBACK_DATA,
                                )
                            ]
                        )
                        return keyboard
                    case _:
                        raise FieldHandleError(f"Unexpected repeat type: {self._habit_buffer.repeat_type}")
            case _:
                raise FieldHandleError(f"Unexpected state: {self.__state}")


class NotificationsFieldState(IFieldState):
    field = HabitField.notifications
    SUBMIT_CALLBACK_DATA = 'NOTIFICATION_FIELD_STATE_SUBMIT'
    DELETE_PREFIX = 'delete'

    async def handle(self, text: str) -> IFieldState:
        if self._habit_buffer.notifications is None:
            self._habit_buffer.notifications = []

        if text == self.SUBMIT_CALLBACK_DATA:
            return NameFieldState(self._habit_buffer, self._backend_repository, self._user_cache)

        try:
            to_delete = False
            if text.startswith(self.DELETE_PREFIX):
                to_delete = True
                text = text.lstrip(self.DELETE_PREFIX)

            notification = datetime.time.fromisoformat(text)
            notification = local_to_utc(notification, self._user_cache.timezone)

            if to_delete:
                self._habit_buffer.notifications.remove(notification)
            else:
                self._habit_buffer.notifications.append(notification)
            self._habit_buffer.notifications.sort()
        except Exception as e:
            logger.exception(e)
            raise FieldHandleError(f"Could not deduct time from '{text}'")

        return self

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message, FieldStateInputType.callback_query)

    def keyboard(self) -> list[list[InlineKeyboardButton]] | None:
        l = localizator.localizator.lang(self._user_cache.language)
        keyboard = []

        if self._habit_buffer.notifications:
            for notification in self._habit_buffer.notifications:
                notification = utc_to_local(notification, self._user_cache.timezone)

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f'🗑 {notification.strftime("%H:%M")}',
                            callback_data=f'{self.DELETE_PREFIX}{notification}',
                        )
                    ]
                )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=l.button_next,
                    callback_data=self.SUBMIT_CALLBACK_DATA,
                )
            ]
        )
        return keyboard


field_states_factory = {
    s.field: s
    for s in (
        NameFieldState,
        DescriptionFieldState,
        TimesPerDayFieldState,
        StartDateFieldState,
        EndDateFieldState,
        RepeatTypeFieldState,
        NotificationsFieldState,
    )
}
