from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.util import await_only

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.menu import setup_menu
from config import MONTHS

from bot.state_machine.istate import IState
from .abstract_habits_list_state import AbstractHabitsListState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.my_habits)
class MyHabitsState(AbstractHabitsListState):
    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        await callback_query.answer()

        if callback_query.data in (self.SCROLL_LEFT, self.SCROLL_RIGHT):
            self._handel_pages(callback_query.data)
        elif callback_query.data.startswith('habit'):
            _, habit_id = callback_query.data.split('_')
            return self._create(HabitStates.edit_habit, habit_id=int(habit_id))

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
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        start = (self._page_current - 1) * self.HABITS_PER_PAGE
        end = start + self.HABITS_PER_PAGE

        for habit in self._habits[start:end]:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f'{habit.name}',
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
