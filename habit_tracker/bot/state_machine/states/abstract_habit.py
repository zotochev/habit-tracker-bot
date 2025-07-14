from __future__ import annotations

import inspect
import datetime
from abc import abstractmethod
from enum import StrEnum, auto
import logging

from pydantic import ValidationError
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import dateparser

from core import localizator
from data.schemas import HabitBuffer

from bot.states import HabitStates
from bot.state_machine.states_interfaces import IState
from bot.state_machine.states_interfaces import ISuspendableState

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


class FieldHandleError(Exception):
    pass


class AbstractHabitState(IState, ISuspendableState):
    order = (
        HabitField.name,
        HabitField.description,
        HabitField.times_per_day,
        HabitField.start_date,
        HabitField.end_date,
    )

    HABIT_BUTTON_SUBMIT = 'habit_button_submit'
    HABIT_BUTTON_BACK = 'habit_button_back'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        # self._habit_message: Message | None = None

        self._current_field = HabitField.name
        last_date = user_cache.last_datetime.date() if user_cache.last_datetime else None
        self._habit = HabitBuffer(
            start_date=last_date
        )
        self._fields_handlers = {
            HabitField.name: self._handle_name,
            HabitField.start_date: self.__handle_date,
            HabitField.end_date: self.__handle_date,
            HabitField.times_per_day: self.__handle_times_per_day
        }
        self.__last_error: str | None = None

    async def _handle_message(self, message: Message) -> IState:
        if self._habit.start_date is None:
            self._habit.start_date = message.date.date()

        try:
            field_data = self._fields_handlers.get(self._current_field, lambda x: x)(message.text)
            if inspect.iscoroutine(field_data):
                field_data = await field_data
            setattr(self._habit, self._current_field, field_data)
            self.__set_next_state()
            await self.__update_habit_message()
        except FieldHandleError:
            await self.__update_habit_message()
        except ValidationError as e:
            logger.warning(f"{self.__class__.__name__}._handle_message {e.__class__.__name__}: {e}")
        except Exception as e:
            logger.warning(f"{self.__class__.__name__}._handle_message {e.__class__.__name__}: {e}")

        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        if callback_query.data == self.HABIT_BUTTON_SUBMIT:
            await self._handle_submit(callback_query)
            return self._create(HabitStates.end)
        elif callback_query.data == self.HABIT_BUTTON_BACK:
            return self._create(HabitStates.end)
        elif self._current_field != HabitField(callback_query.data):
            self._current_field = HabitField(callback_query.data)
            await self.__update_habit_message()
            await callback_query.answer()
        else:
            await callback_query.answer()
        return self

    @abstractmethod
    async def _handle_submit(self, callback_query: CallbackQuery):
        raise NotImplementedError

    async def _handle(self):
        return self

    async def on_enter(self) -> None:
        """
        New Habit

        name: {}
        description: {}
        times per day: {}
        start: {}
        end: {}
        """
        await super().on_enter()
        await self.__update_habit_message()

    async def on_restore(self) -> None:
        await super().on_restore()
        await self.__update_habit_message()

    async def on_suspend(self) -> None:
        await super().on_suspend()

    def _is_habit_ready(self):
        return self._habit.name is not None

    @abstractmethod
    def _get_message_header(self) -> str:
        raise NotImplementedError

    def __set_next_state(self):
        if self._current_field != self.order[-1]:
            self._current_field = self.order[self.order.index(self._current_field) + 1]

    async def _handle_name(self, habit_name: str) -> str:
        habit = await self._backend_repository.get_habit_by_user_id_and_name(self._user_cache.backend_id, habit_name)
        if habit is not None:
            l = localizator.localizator
            self.__last_error = l.lang(self._user_cache.language).habit_error_name_already_in_use
            raise FieldHandleError()
        return habit_name

    def __handle_times_per_day(self, number: str) -> str:
        try:
            int(number)
        except Exception:
            l = localizator.localizator
            self.__last_error = l.lang(self._user_cache.language).habit_error_times
            raise FieldHandleError()
        return number

    def __handle_date(self, date_text: str) -> datetime.date | None:
        try:
            return dateparser.parse(date_text).date()
        except Exception:
            l = localizator.localizator
            self.__last_error = l.lang(self._user_cache.language).habit_error_date
            raise FieldHandleError()

    async def __update_habit_message(self):
        self.__update_start_habit_time()
        text, reply_markup = self.__create_habit_message()
        await self._user_cache.messanger.update_main_message(text, reply_markup)

    def __update_start_habit_time(self) -> None:
        if (
                self._user_cache is None
                or self._user_cache.last_datetime is None
                or self._habit.start_date is not None
        ):
            return
        self._habit.start_date = self._user_cache.last_datetime.date()

    def _get_submit_button_text(self) -> str:
        raise NotImplementedError

    def __create_habit_message(self):
        l = localizator.localizator.lang(self._user_cache.language)
        translations = {
            HabitField.name: l.habit_field_name,
            HabitField.description: l.habit_field_description,
            HabitField.times_per_day: l.habit_field_times_per_day,
            HabitField.start_date: l.habit_field_start_date,
            HabitField.end_date: l.habit_field_end_date,

            self.HABIT_BUTTON_SUBMIT: self._get_submit_button_text(),
        }

        text = self._get_message_header()

        text += "\n".join(
            "{}{}: {}".format(
                '> ' if h == self._current_field else '',
                translations[h],
                getattr(self._habit, h) if getattr(self._habit, h, None) else '-'
            )
            for h in self.order
        )
        if self.__last_error is not None:
            text += '\n'
            text += self.__dump_last_error()

        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=translations[habit_field],
                    callback_data=habit_field,
                ),
            ] for habit_field in self.order
        ])

        if self._is_habit_ready():
            reply_markup.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=translations[self.HABIT_BUTTON_SUBMIT],
                        callback_data=self.HABIT_BUTTON_SUBMIT,
                    ),
                ]
            )

        reply_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=l.button_back,
                    callback_data=self.HABIT_BUTTON_BACK,
                ),
            ]
        )

        return text, reply_markup

    def __dump_last_error(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        formated_error = '{}: {}'.format(l.habit_error_header, self.__last_error)
        self.__last_error = None
        return formated_error
