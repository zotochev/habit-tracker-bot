from __future__ import annotations
import logging
import datetime

from aiogram.types import Message, CallbackQuery

from core import localizator
import bot
from bot.states import HabitStates
from bot.state_machine.istate import IState
from bot.state_machine.states_factory import register_state

from typing import TYPE_CHECKING

from data.schemas import CommonProgress

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.progress)
class ProgressState(IState):
    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        # self._progress_message: Message | None = None

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        return await self._handle()

    async def _handle(self):
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        text = await self.__create_text()

        await self._user_cache.messanger.update_main_message(text)
        # self._progress_message = await bot.bot_instance.send_message(
        #     chat_id=self._user_cache.telegram_id,
        #     text=text,
        #     # reply_markup=reply_markup,
        # )

    async def on_exit(self) -> None:
        await super().on_enter()

    async def __create_text(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)
        progress = await self.__get_progress_data()

        result = (
            f'{l.menu_progress}\n'
            f'{self.__get_daily_tagline()}\n\n'
            f"{l.progress_total_habits}: {progress.habit_count}\n"
            f"{l.progress_day}: {progress.today_done} / {progress.today_expected}\n"
            f"{l.progress_overall}: {progress.percent_complete}% ({progress.total_completed} / {progress.total_expected})\n"
            f"{l.progress_week}: {progress.week_done} / {progress.week_expected}\n"
            f"{l.progress_month}: {progress.month_done} / {progress.month_expected}"
        )

        return result

    async def __get_progress_data(self) -> CommonProgress | None:
        return await self._backend_repository.get_all_habits_statistics(
            user_id=self._user_cache.backend_id,
            today=self._user_cache.last_datetime.date(),
        )


    def __get_daily_tagline(self):
        taglines = localizator.localizator.lang(self._user_cache.language).progress_taglines

        today = datetime.date.today()
        # Convert date to a simple int value (e.g., 20250622)
        date_number = int(today.strftime('%Y%m%d'))
        # Use modulo to select tagline index
        index = date_number % len(taglines)
        return taglines[index]
