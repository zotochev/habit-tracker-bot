from __future__ import annotations
import logging
import datetime

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.state_machine.states.abstract_habit import AbstractHabitState
from core import localizator
import bot
from bot.states import HabitStates
from bot.state_machine.istate import IState
from bot.state_machine.states_factory import register_state

from typing import TYPE_CHECKING

from data.schemas import HabitUpdate
from data.schemas.habit_event import HabitStatistics

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.progress_habit)
class ProgressHabitState(IState):
    BACK_BUTTON_CALLBACK_DATA = 'back'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 habit_id: int,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._habit_id = habit_id
        self._habit: HabitUpdate | None = None

    async def on_enter(self) -> None:
        await super().on_enter()
        self._habit = await self.__retrieve_habit()

        text = await self.__create_text()
        keyboard = self.__create_keyboard()

        await self._user_cache.messanger.update_main_message(text, keyboard)

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        if callback_query.data == self.BACK_BUTTON_CALLBACK_DATA:
            await callback_query.answer()
            return self._create(HabitStates.end)
        return await self._handle()

    async def _handle(self):
        return self

    async def on_exit(self) -> None:
        await super().on_enter()

    async def __get_stats(self, target_date: datetime.date) -> HabitStatistics:
        user_id = self._user_cache.backend_id

        return await self._backend_repository.get_habit_statistics(user_id, self._habit_id, target_date)

    async def __create_text(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)
        s = await self.__get_stats(self._user_cache.last_datetime.date())

        return (
            f"📈 {self._habit.name}\n\n"
            f"{l.progress_overall}: {s.percent_complete}%\n"
            f"{l.progress_day}: {int(s.today_done * 100 / s.times_per_day)}% -  {s.today_done} / {s.times_per_day}\n"
            f"{l.progress_streak}: {s.current_streak}\n\n"
            f"{l.progress_week}: {int(s.week_done * 100 / s.week_expected)}%\n"
            f"{l.progress_month}: {int(s.month_done * 100 / s.month_expected)}%"
        )

    def __get_daily_tagline(self):
        taglines = localizator.localizator.lang(self._user_cache.language).progress_taglines

        today = datetime.date.today()
        # Convert date to a simple int value (e.g., 20250622)
        date_number = int(today.strftime('%Y%m%d'))
        # Use modulo to select tagline index
        index = date_number % len(taglines)
        return taglines[index]

    async def __retrieve_habit(self) -> HabitUpdate:
        return await self._backend_repository.get_habit_by_user_id_and_id(self._user_cache.backend_id, self._habit_id)

    def __create_keyboard(self) -> InlineKeyboardMarkup:
        l = localizator.localizator.lang(self._user_cache.language)

        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=l.button_back,
                callback_data=self.BACK_BUTTON_CALLBACK_DATA,
            ),
        ]])

