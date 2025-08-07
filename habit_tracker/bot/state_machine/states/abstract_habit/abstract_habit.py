from __future__ import annotations

from abc import abstractmethod
import logging

from pydantic import ValidationError
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core import localizator
from data.schemas import HabitBuffer, HabitRepeatType

from bot.states import HabitStates
from bot.state_machine.states_interfaces import IState
from bot.state_machine.states_interfaces import ISuspendableState

from .habit_field_enum import HabitField
from .abstract_habit_field_states import IFieldState
from .exceptions import FieldHandleError
from .abstract_habit_field_states import (
    NameFieldState,
    field_states_factory,
    FieldStateInputType,
)

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


class AbstractHabitState(IState, ISuspendableState):
    HABIT_BUTTON_SUBMIT = 'habit_button_submit'
    HABIT_BUTTON_BACK = 'habit_button_back'

    def __init__(
        self,
        backend_repository: BackendRepository,
        user_cache: UserCache,
        state_factory: dict[HabitStates, type[IState]],
    ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        last_date = user_cache.last_datetime.date() if user_cache.last_datetime else None
        self._habit = HabitBuffer(start_date=last_date)
        self._current_field: IFieldState = NameFieldState(self._habit, self._backend_repository, self._user_cache)
        self.__last_error: str | None = None

    async def __process_input(self, text: str) -> None:
        try:
            self._current_field = await self._current_field.handle(text)
            await self.__update_habit_message()
        except FieldHandleError as e:
            self.__last_error = str(e)
            await self.__update_habit_message()
        except ValidationError as e:
            logger.warning(f"{self.__class__.__name__}._handle_message {e.__class__.__name__}: {e}")
        except Exception as e:
            logger.warning(f"{self.__class__.__name__}._handle_message {e.__class__.__name__}: {e}")
            logger.exception(e)

    async def _handle_message(self, message: Message) -> IState:
        if self._habit.start_date is None:
            self._habit.start_date = message.date.date()

        if not self._current_field.is_expected_input_type(FieldStateInputType.message):
            l = localizator.localizator
            self.__last_error = l.lang(self._user_cache.language).habit_error_repeat_type_use_keyboard
            await self.__update_habit_message()
            return await self._handle()

        await self.__process_input(message.text)
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        if callback_query.data == self.HABIT_BUTTON_SUBMIT:
            await self._handle_submit(callback_query)
            return self._create(HabitStates.end)
        elif callback_query.data == self.HABIT_BUTTON_BACK:
            return self._create(HabitStates.end)
        elif self._current_field.is_expected_input_type(FieldStateInputType.callback_query):
            await self.__process_input(callback_query.data)
            await callback_query.answer()
        elif self._current_field.field != HabitField(callback_query.data):
            self._current_field = field_states_factory[HabitField(callback_query.data)](self._habit, self._backend_repository, self._user_cache)
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
            HabitField.repeat_type: l.habit_repeat_type,
            HabitField.notifications: l.habit_field_notifications,

            HabitRepeatType.daily: l.habit_repeat_type_daily,
            HabitRepeatType.weekly: l.habit_repeat_type_weekly,
            HabitRepeatType.monthly: l.habit_repeat_type_monthly,

            self.HABIT_BUTTON_SUBMIT: self._get_submit_button_text(),
        }

        def translate_value(key: HabitField, value: Any) -> Any:
            if key == HabitField.repeat_type:
                return translations[value]
            elif key == HabitField.notifications:
                if value:
                    return ", ".join(t.strftime("%H:%M") for t in value)
                else:
                    '-'
            return value

        text = self._get_message_header()

        text += "\n".join(
            "{}{}: {}".format(
                '▶️ ' if h == self._current_field.field else '',
                translations[h],
                translate_value(h, getattr(self._habit, h)) if getattr(self._habit, h, None) else '-'
            )
            for h in field_states_factory
        )
        if self.__last_error is not None:
            text += '\n'
            text += self.__dump_last_error()

        reply_markup = InlineKeyboardMarkup(inline_keyboard=[])
        field_keyboard = self._current_field.keyboard()

        if field_keyboard is not None:
            reply_markup.inline_keyboard = field_keyboard
        else:
            reply_markup.inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=translations[habit_field],
                        callback_data=habit_field,
                    ),
                ] for habit_field in field_states_factory
            ]

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

    # async def __handle_repeat_type(self, repeat_type: str) -> HabitRepeatType:
    #     l = localizator.localizator.lang(self._user_cache.language)
    #     try:
    #         return HabitRepeatType(int(repeat_type))
    #     except Exception as e:
    #         logger.error(f"{self.__class__.__name__}.__handle_repeat_type({repeat_type}) -> {e.__class__.__name__}: {e}")
    #         self.__last_error = l.habit_repeat_invalid_input
    #         raise FieldHandleError()
