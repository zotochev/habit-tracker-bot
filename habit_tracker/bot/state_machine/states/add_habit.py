from __future__ import annotations

import inspect
import datetime
from enum import StrEnum, auto
import logging

from pydantic import ValidationError
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import dateparser

from bot import bot_instance
from bot.menu import setup_menu
from bot.states import HabitStates
import bot
from core import localizator
from data.schemas import HabitBuffer

from bot.state_machine.istate import IState
from bot.state_machine.states_factory import register_state

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
class AddHabitState(IState):
    order = (
        HabitField.name,
        HabitField.description,
        HabitField.times_per_day,
        HabitField.start_date,
        HabitField.end_date,
    )

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._habit_message: Message | None = None

        self._current_field = HabitField.name
        last_date = user_cache.last_datetime.date() if user_cache.last_datetime else None
        self._habit = HabitBuffer(
            start_date=last_date
        )
        self._fields_handlers = {
            HabitField.name: self.__handle_name,
            HabitField.start_date: self.__handle_date,
            HabitField.end_date: self.__handle_date,
            HabitField.times_per_day: self.__handle_times_per_day
        }
        self.__last_error: str | None = None

    async def _handle_message(self, message: Message) -> IState:
        await message.delete()

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
        if callback_query.data == HABIT_BUTTON_SUBMIT:
            await self._backend_repository.create_habit(self._user_cache.backend_id, self._habit)
            await callback_query.answer()
            await callback_query.message.delete()
            return self._create(HabitStates.end)
        elif self._current_field != HabitField(callback_query.data):
            self._current_field = HabitField(callback_query.data)
            await self.__update_habit_message()

        await callback_query.answer()
        return self

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

        self._habit_message: Message | None = None

        self._current_field = HabitField.name
        self._habit = HabitBuffer()

        await self.__update_habit_message()

    async def on_restore(self) -> None:
        await super().on_restore()
        await self.__update_habit_message()

    def _is_habit_ready(self):
        return self._habit.name is not None

    def __set_next_state(self):
        if self._current_field != self.order[-1]:
            self._current_field = self.order[self.order.index(self._current_field) + 1]

    async def __handle_name(self, habit_name: str) -> str:
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
        try:
            if self._habit_message is not None:
                await self._habit_message.edit_text(text, reply_markup=reply_markup)
            else:
                self._habit_message = await bot.bot_instance.send_message(
                    chat_id=self._user_cache.telegram_id,
                    text=text,
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logger.warning(f"{self.__class__.__name__}._handle_callback_query {e.__class__.__name__}: {e}")
            self._habit_message = await bot.bot_instance.send_message(
                chat_id=self._user_cache.telegram_id,
                text=text,
                reply_markup=reply_markup,
            )

    def __update_start_habit_time(self) -> None:
        if (
                self._user_cache is None
                or self._user_cache.last_datetime is None
                or self._habit.start_date is not None
        ):
            return
        self._habit.start_date = self._user_cache.last_datetime.date()

    def __create_habit_message(self):
        l = localizator.localizator
        translations = {
            HabitField.name: l.lang(self._user_cache.language).habit_field_name,
            HabitField.description: l.lang(self._user_cache.language).habit_field_description,
            HabitField.times_per_day: l.lang(self._user_cache.language).habit_field_times_per_day,
            HabitField.start_date: l.lang(self._user_cache.language).habit_field_start_date,
            HabitField.end_date: l.lang(self._user_cache.language).habit_field_end_date,

            HABIT_BUTTON_SUBMIT: l.lang(self._user_cache.language).habit_button_submit
        }

        text = f"{l.lang(self._user_cache.language).habit_header}\n"
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
                        text=translations[HABIT_BUTTON_SUBMIT],
                        callback_data=HABIT_BUTTON_SUBMIT,
                    ),
                ]
            )

        return text, reply_markup

    def __dump_last_error(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        formated_error = '{}: {}'.format(l.habit_error_header, self.__last_error)
        self.__last_error = None
        return formated_error
