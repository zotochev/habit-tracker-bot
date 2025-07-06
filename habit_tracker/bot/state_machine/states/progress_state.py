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

from data.schemas.habit_event import HabitStatistics

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
        self._progress_message: Message | None = None

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        return await self._handle()

    async def _handle(self):
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        text = await self.__create_text()

        self._progress_message = await bot.bot_instance.send_message(
            chat_id=self._user_cache.telegram_id,
            text=text,
            # reply_markup=reply_markup,
        )

    async def on_exit(self) -> None:
        await super().on_enter()

    async def __create_text(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        result = ''
        result += f'{l.menu_progress}\n'
        result += f'{self.__get_daily_tagline()}\n'
        result += f'\n'
        result += f'{l.progress_overall}: 76% (выполнено 128 из 168)\n'
        result += f'{l.progress_day}: 5 из 7 (71%)\n'
        result += f'{l.progress_week}: 22 из 30 (73%)\n'
        result += f'{l.progress_month}: 54 из 65 (83%)\n'
        result += f'\n'
        result += f'{l.progress_best_habit}: Пить воду — выполнена в 95% дней\n'
        result += f'{l.progress_worst_habit}: Растяжка — только 42%\n'
        result += f'{l.progress_weekly_trend}: +6% по сравнению с прошлой неделей!\n'

        return result

    def __get_daily_tagline(self):
        taglines = localizator.localizator.lang(self._user_cache.language).progress_taglines

        today = datetime.date.today()
        # Convert date to a simple int value (e.g., 20250622)
        date_number = int(today.strftime('%Y%m%d'))
        # Use modulo to select tagline index
        index = date_number % len(taglines)
        return taglines[index]
