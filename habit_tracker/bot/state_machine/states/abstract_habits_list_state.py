from __future__ import annotations
import logging
from abc import abstractmethod

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from bot.states import HabitStates

from bot.state_machine.states_interfaces import IState
from bot.state_machine.states_interfaces import ISuspendableState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.schemas import Habit
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


class AbstractHabitsListState(IState, ISuspendableState):
    HABITS_PER_PAGE = 10
    SCROLL_LEFT = '<'
    SCROLL_RIGHT = '>'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._pages_total = None
        self._page_current = None
        self._habits = None

    async def handle(self, message: Message | CallbackQuery) -> IState:
        return await super().handle(message)

    async def on_restore(self) -> None:
        await super().on_restore()
        await self.__update()

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    def _handel_pages(self, data: str):
        if data == self.SCROLL_RIGHT:
            if self._page_current == self._pages_total:
                self._page_current = 1
            else:
                self._page_current += 1
        elif data == self.SCROLL_LEFT:
            if self._page_current == 1:
                self._page_current = self._pages_total
            else:
                self._page_current -= 1

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        if callback_query.data in (self.SCROLL_LEFT, self.SCROLL_RIGHT):
            self._handel_pages(callback_query.data)
        elif callback_query.data.startswith('habit'):
            await self._process_habit_button_callback(callback_query)

        await callback_query.answer()

        return await self._handle()

    async def _update_message(self):
        text = self._format_habits_message()
        keyboard = self._construct_keyboard()

        await self._user_cache.messenger.update_main_message(text, keyboard)

    @abstractmethod
    async def _process_habit_button_callback(self, callback_query: CallbackQuery) -> None:
        raise NotImplementedError

    def __is_habit_completed(self, habit_id: int) -> bool:
        for habit in self._habits:
            if habit.id == habit_id:
                return habit.times_did + 1 == habit.times_per_day
        return False

    async def _handle(self):
        await self.__update()
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        await self.__update()

    async def on_exit(self) -> None:
        await super().on_exit()

    def _format_habits_message(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def _retrieve_habits(self) -> Habit:
        raise NotImplementedError

    async def __update(self) -> None:
        habits = await self._retrieve_habits()
        self._habits = habits or []

        self.__update_pages_number()
        await self._update_message()

    def __update_pages_number(self):
        number_of_habits = len(self._habits)
        self._pages_total = max(1, (number_of_habits + self.HABITS_PER_PAGE - 1) // self.HABITS_PER_PAGE)
        if self._page_current is None:
            self._page_current = 1
        self._page_current = min(self._page_current, self._pages_total)

    def _construct_keyboard(self) -> InlineKeyboardMarkup:
        raise NotImplementedError
