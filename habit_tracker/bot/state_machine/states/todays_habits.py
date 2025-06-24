from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.menu import setup_menu
from config import MONTHS

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.todays_habits)
class TodaysHabitsState(IState):
    HABITS_PER_PAGE = 10
    SCROLL_LEFT = '<'
    SCROLL_RIGHT = '>'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._list_message: Message | None = None
        self._pages_total = None
        self._page_current = None
        self._habits = None

    async def _handle_message(self, message: Message) -> IState:
        await message.delete()
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        kw = {}
        l = localizator.localizator.lang(self._user_cache.language)

        if callback_query.data == self.SCROLL_RIGHT:
            if self._page_current == self._pages_total:
                self._page_current = 1
            else:
                self._page_current += 1
        if callback_query.data == self.SCROLL_LEFT:
            if self._page_current == 1:
                self._page_current = self._pages_total
            else:
                self._page_current -= 1
        if callback_query.data.startswith('habit'):
            _, habit_id = callback_query.data.split('_')
            await self._backend_repository.send_habit_event(int(habit_id), self._user_cache.last_datetime.date())
            if self.__is_habit_completed(int(habit_id)):
                kw = {'text': l.habit_list_congrats, 'show_alert': False}
        await callback_query.answer(**kw)

        result = await self._handle()
        text = self.__format_habits_message()
        await self.__edit_habits_message(text)
        return result

    def __is_habit_completed(self, habit_id: int) -> bool:
        for habit in self._habits:
            if habit.id == habit_id:
                return habit.times_did + 1 == habit.times_per_day
        return False

    async def _handle(self):
        await self.__update()
        return self

    async def on_restore(self) -> None:
        await super().on_restore()
        await self.__update()
        text = self.__format_habits_message()
        await self.__send_habits_message(text)

    async def on_enter(self) -> None:
        await super().on_enter()
        await self.__update()
        text = self.__format_habits_message()
        await self.__send_habits_message(text)

    def __format_habits_message(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)

        text = ''
        text += f'📅 {l.habit_list_header} — {MONTHS[self._user_cache.language][self._user_cache.last_datetime.month]} {self._user_cache.last_datetime.day}\n'
        text += f'{l.habit_list_tagline}\n'
        text += f'{l.habit_list_page}: [{self._page_current}/{self._pages_total}]\n'
        text += '\n'
        text += '\n'

        if not self._habits:
            text = f'\n{l.habit_list_no_habits}'
            return text
        return text

    async def __send_habits_message(self, message: str) -> None:
        if self._list_message is not None:
            try:
                await self._list_message.delete()
            except Exception as e:
                logger.warning(f"__send_habits_message: {e.__class__.__name__}: {e}")

        self._list_message = await bot.bot_instance.send_message(
            chat_id=self._user_cache.telegram_id,
            text=message,
            reply_markup=self.__construct_keyboard(),
        )

    async def __edit_habits_message(self, message: str) -> None:
        if self._list_message is not None:
            try:
                if self._list_message.text != message:
                    await self._list_message.edit_text(
                        text=message,
                        reply_markup=self.__construct_keyboard(),
                    )
            except Exception as e:
                logger.warning(f"__edit_habits_message: {e.__class__.__name__}: {e}")
                await self.__send_habits_message(message)

    async def __update(self) -> None:
        habits = await self._backend_repository.get_habits_for_date(
            self._user_cache.backend_id, self._user_cache.last_datetime.date(), unfinished_only=True
        )
        self._habits = habits or []
        number_of_habits = len(self._habits)

        self._pages_total = max(1, (number_of_habits + self.HABITS_PER_PAGE - 1) // self.HABITS_PER_PAGE)

        if self._page_current is None:
            self._page_current = 1
        self._page_current = min(self._page_current, self._pages_total)

    def __construct_keyboard(self):
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
