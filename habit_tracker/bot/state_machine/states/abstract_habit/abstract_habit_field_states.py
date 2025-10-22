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
from data.schemas.translations import Translations

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
    next_state: type[IFieldState]

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache,
    ) -> None:
        assert self.next_state is not None
        self._habit_buffer = habit_buffer
        self._notifications = notifications
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

    @staticmethod
    def translate_name(l: Translations) -> str:
        raise NotImplementedError

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        raise NotImplementedError


class NameFieldState(IFieldState):
    field = HabitField.name

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        self.next_state = DescriptionFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    async def handle(self, text: str) -> IFieldState:
        habit_name = text
        habit = await self._backend_repository.get_habit_by_user_id_and_name(self._user_cache.backend_id, habit_name)
        if habit is not None:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_name_already_in_use)
        self._habit_buffer.name = habit_name
        return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_name

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        return habit.name if habit.name else '-'


class DescriptionFieldState(IFieldState):
    field = HabitField.description

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        self.next_state = StartDateFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    async def handle(self, text: str) -> IFieldState:
        self._habit_buffer.description = text
        return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_description

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        return habit.description if habit.description else '-'


class TimesPerDayFieldState(IFieldState):
    field = HabitField.times_per_day

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    async def handle(self, text: str) -> IFieldState:
        try:
            self._habit_buffer.times_per_day = int(text)
        except Exception:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_times)
        return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_times_per_day

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        number = 1
        if habit.notifications:
            number = len(habit.notifications)
        return str(number)


class DateFieldState(IFieldState):
    async def handle(self, text: str) -> IFieldState:
        try:
            self._set_field(dateparser.parse(text).date())
        except Exception:
            l = localizator.localizator
            raise FieldHandleError(l.lang(self._user_cache.language).habit_error_date)
        return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

    @abstractmethod
    def _set_field(self, field_date: datetime.date) -> None:
        ...

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message,)


class StartDateFieldState(DateFieldState):
    field = HabitField.start_date

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        self.next_state = EndDateFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    def _set_field(self, field_date: datetime.date) -> None:
        self._habit_buffer.start_date = field_date

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_start_date

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        date_text = '-'
        if habit.start_date:
            date_text = str(habit.start_date)
        return date_text


class EndDateFieldState(DateFieldState):
    field = HabitField.end_date

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        self.next_state = RepeatTypeFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    def _set_field(self, field_date: datetime.date) -> None:
        self._habit_buffer.end_date = field_date

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_end_date

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        date_text = '-'
        if habit.end_date:
            date_text = str(habit.end_date)
        return date_text


class RepeatTypeFieldState(IFieldState):
    field = HabitField.repeat_type

    TYPE_STATE = 0
    DAYS_STATE = 1

    SUBMIT_CALLBACK_DATA = 'REPEAT_TYPE_FIELD_STATE_SUBMIT'

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache,
    ) -> None:
        self.next_state = NotificationsFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)
        self.__state = self.TYPE_STATE

    async def handle(self, text: str) -> IFieldState:
        l = localizator.localizator.lang(self._user_cache.language)

        if text == self.SUBMIT_CALLBACK_DATA:
            return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

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

        return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

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

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_repeat_type

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        repeat_name = '-'
        match habit.repeat_type:
            case HabitRepeatType.daily:
                repeat_name = l.habit_repeat_type_daily
            case HabitRepeatType.weekly:
                repeat_name = l.habit_repeat_type_weekly
            case HabitRepeatType.monthly:
                repeat_name = l.habit_repeat_type_monthly
        return repeat_name


class NotificationsFieldState(IFieldState):
    field = HabitField.notifications
    SUBMIT_CALLBACK_DATA = 'NOTIFICATION_FIELD_STATE_SUBMIT'
    DELETE_PREFIX = 'delete'
    MAX_NOTIFICATIONS = 10

    def __init__(
            self,
            habit_buffer: HabitBuffer,
            notifications: list[datetime.time],
            backend_repository: BackendRepository,
            user_cache: UserCache) -> None:
        self.next_state = NameFieldState
        super().__init__(habit_buffer, notifications, backend_repository, user_cache)

    async def handle(self, text: str) -> IFieldState:
        l = localizator.localizator.lang(self._user_cache.language)

        if text == self.SUBMIT_CALLBACK_DATA:
            return self.next_state(self._habit_buffer, self._notifications, self._backend_repository, self._user_cache)

        try:
            to_delete = False
            if text.startswith(self.DELETE_PREFIX):
                to_delete = True
                text = text.lstrip(self.DELETE_PREFIX)

            notification = datetime.time.fromisoformat(text)
            notification = local_to_utc(notification, self._user_cache.timezone)
            is_max_number_of_notifications = len(self._notifications) >= self.MAX_NOTIFICATIONS

            if to_delete:
                self._notifications.remove(notification)
            elif is_max_number_of_notifications:
                raise FieldHandleError(f"{l.exceeded_max_number_of_notifications}: {self.MAX_NOTIFICATIONS}")
            elif not is_max_number_of_notifications:
                self._notifications.append(notification)

            self._habit_buffer.times_per_day = max(1, len(self._notifications))
            self._notifications.sort()
        except ValueError as e:
            logger.exception(e)
            raise FieldHandleError(f"{l.could_not_deduct_time_from_input} '{text}'")
        except Exception as e:
            logger.exception(e)
            raise FieldHandleError(f"Unexpected error '{text}'")

        return self

    def is_expected_input_type(self, input_type: FieldStateInputType) -> bool:
        return input_type in (FieldStateInputType.message, FieldStateInputType.callback_query)

    def keyboard(self) -> list[list[InlineKeyboardButton]] | None:
        l = localizator.localizator.lang(self._user_cache.language)
        keyboard = []

        if self._notifications:
            for notification in self._notifications:
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

    @staticmethod
    def translate_name(l: Translations) -> str:
        return l.habit_field_notifications

    @staticmethod
    def translate_value(l: Translations, habit: HabitBuffer, notifications: list[datetime.time], user_cache: UserCache) -> str:
        if not notifications:
            return '-'
        return ", ".join(utc_to_local(t, user_cache.timezone).strftime("%H:%M") for t in notifications)


field_states_order = (
    NameFieldState,
    DescriptionFieldState,
    StartDateFieldState,
    EndDateFieldState,
    RepeatTypeFieldState,
    NotificationsFieldState,
)
field_states_factory = {s.field: s for s in field_states_order}
