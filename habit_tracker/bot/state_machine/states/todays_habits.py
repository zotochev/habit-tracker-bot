from __future__ import annotations
import logging

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from core import localizator

from .abstract_habits_list_state import AbstractHabitsListState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from bot.state_machine.states_interfaces import IState
    from data.schemas import HabitProgress
    from data.repositories.backend_repository.backend_repository import BackendRepository

logger = logging.getLogger(__name__)


# @register_state(HabitStates.todays_habits)
class TodaysHabitsState(AbstractHabitsListState):
    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, type[IState]],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self.__has_habits_today = False

    async def _process_habit_button_callback(self, callback_query: CallbackQuery) -> None:
        l = localizator.localizator.lang(self._user_cache.language)
        kw = {}

        _, habit_id = callback_query.data.split('_')
        await self._backend_repository.send_habit_event(int(habit_id), self._user_cache.last_datetime.date())
        if self.__is_habit_completed(int(habit_id)):
            kw = {'text': l.habit_list_congrats, 'show_alert': False}
        await callback_query.answer(**kw)

    def __is_habit_completed(self, habit_id: int) -> bool:
        for habit in self._habits:
            if habit.id == habit_id:
                return habit.times_did + 1 == habit.times_per_day  # +1 because habit does not updated yet
        return False

    def _format_habits_message(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        text = ''
        text += f'📅 {l.habit_list_header} — {l.months[self._user_cache.last_datetime.month]} {self._user_cache.last_datetime.day}\n'
        text += f'{l.habit_list_tagline}\n'
        text += f'{l.habit_list_page}: [{self._page_current}/{self._pages_total}]\n'
        text += '\n'
        text += '\n'

        if not self._habits:
            if not self.__has_habits_today:
                text = f'\n{l.habit_list_no_habits_today}'
            elif self.__has_habits_today:
                text = f'\n{l.habit_list_you_did_all_habits_today}'
            else:
                text = '\nUnexpected 🐕'
        return text

    async def _retrieve_habits(self) -> list[HabitProgress]:
        habits = await self._backend_repository.get_habits_for_date(
            self._user_cache.backend_id, self._user_cache.last_datetime.date(), unfinished_only=False
        )
        self.__has_habits_today = len(habits) > 0
        return [h for h in habits if h.times_did < h.times_per_day]

    def _construct_keyboard(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        start = (self._page_current - 1) * self.HABITS_PER_PAGE
        end = start + self.HABITS_PER_PAGE

        for habit in self._habits[start:end]:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f'{habit.name} {habit.times_did}/{habit.times_per_day}',
                        callback_data=f'habit_{habit.id}',
                    ),
                ]
            )

        if self._pages_total > 1:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=self.SCROLL_LEFT,
                        callback_data=self.SCROLL_LEFT,
                    ),
                    InlineKeyboardButton(
                        text=self.SCROLL_RIGHT,
                        callback_data=self.SCROLL_RIGHT,
                    ),
                ]
            )
        return keyboard
