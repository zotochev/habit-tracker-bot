from __future__ import annotations
import logging

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from core import localizator

from bot.state_machine.states_interfaces import IState

from .abstract_habits_list_state import AbstractHabitsListState


logger = logging.getLogger(__name__)


@register_state(HabitStates.my_habits)
class MyHabitsState(AbstractHabitsListState):
    HABIT_PROGRESS_CDATA = 'habit_progress'
    HABIT_EDIT_CDATA = 'habit_edit'
    HABIT_DELETE_CDATA = 'habit_delete'

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        await callback_query.answer()

        if callback_query.data in (self.SCROLL_LEFT, self.SCROLL_RIGHT):
            self._handel_pages(callback_query.data)
        elif callback_query.data.startswith(self.HABIT_PROGRESS_CDATA):
            *_, habit_id = callback_query.data.split('_')
            return self._create(HabitStates.progress_habit, habit_id=int(habit_id))
        elif callback_query.data.startswith(self.HABIT_EDIT_CDATA):
            *_, habit_id = callback_query.data.split('_')
            return self._create(HabitStates.edit_habit, habit_id=int(habit_id))
        elif callback_query.data.startswith(self.HABIT_DELETE_CDATA):
            *_, habit_id = callback_query.data.split('_')
            return self._create(HabitStates.delete_habit, habit_id=int(habit_id))

        return await self._handle()

    def _format_habits_message(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        text = ''
        text += f'📋 {l.my_habits_header}\n'
        text += f'{l.my_habits_tagline}\n'
        text += f'{l.habit_list_page}: [{self._page_current}/{self._pages_total}]\n'
        text += '\n'
        text += '\n'

        if not self._habits:
            text = f'\n{l.habit_list_no_habits}'
            return text
        return text

    async def _retrieve_habits(self):
        return await self._backend_repository.get_habits_for_date(
            self._user_cache.backend_id, self._user_cache.last_datetime.date(), unfinished_only=False,
        )

    def _construct_keyboard(self):
        l = localizator.localizator.lang(self._user_cache.language)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        start = (self._page_current - 1) * self.HABITS_PER_PAGE
        end = start + self.HABITS_PER_PAGE

        for habit in self._habits[start:end]:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f'{habit.name}',
                        callback_data=f'{self.HABIT_PROGRESS_CDATA}_{habit.id}',
                    ),
                    InlineKeyboardButton(
                        text=f'{l.my_habits_edit_button}',
                        callback_data=f'{self.HABIT_EDIT_CDATA}_{habit.id}',
                    ),
                    InlineKeyboardButton(
                        text=f'{l.my_habits_delete_button}',
                        callback_data=f'{self.HABIT_DELETE_CDATA}_{habit.id}',
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

    async def _process_habit_button_callback(self, callback_query: CallbackQuery) -> None:
        pass
