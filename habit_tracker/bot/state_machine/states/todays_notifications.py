from __future__ import annotations
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import HabitStates
from bot.state_machine.states_factory import register_state
from bot.state_machine.states_interfaces import IState
from core import localizator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.todays_notifications)
class TodaysNotifications(IState):
    MAX_NOTIFICATIONS = 20

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 **kwargs,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory, **kwargs)
        self._notifications = []
        self._habits = {}

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        l = localizator.localizator.lang(self._user_cache.language)
        _, notification_id = callback_query.data.split('_')

        notification_id = int(notification_id)

        await self._backend_repository.send_habit_event(notification_id, self._user_cache.last_datetime)
        kw = {'text': l.habit_list_congrats, 'show_alert': False}
        await callback_query.answer(**kw)
        return await self._handle()

    async def _handle(self):
        await self.__update()
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        await self.__update()
    
    async def on_exit(self) -> None:
        await super().on_exit()

    async def __update(self) -> None:
        notifications = await self._backend_repository.get_todays_notifications(
            self._user_cache.backend_id,
            datetime.now(ZoneInfo(self._user_cache.timezone)).date(),
        )
        self._notifications = notifications or []
        self._notifications.sort(key=lambda n: (n.time_in_seconds if n.time_in_seconds else float('inf')))

        self._habits.clear()
        habits = await asyncio.gather(*[
            self._backend_repository.get_habit_by_user_id_and_id(self._user_cache.backend_id, n.habit_id)
            for n in self._notifications
        ])
        self._habits = {h.id: h for h in habits}

        await self._update_message()
    
    async def _update_message(self):
        text = self._format_habits_message()
        keyboard = self._construct_keyboard()
        
        await self._user_cache.messenger.update_main_message(text, keyboard)

    def _construct_keyboard(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for n in self._notifications[:self.MAX_NOTIFICATIONS]:
            habit = self._habits[n.habit_id]

            if n.time_in_seconds:
                t = n.time(self._user_cache.timezone)
                print(t, n.time('utc'), self._user_cache.timezone)
                n_time = f'{t.hour:02}:{t.minute:02}' if n.time_in_seconds else '-'
                text = f'{n_time}: {habit.name}'
            else:
                text = f'{habit.name}'

            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f'{self.__class__.__name__}_{n.notification_id}',
                    ),
                ]
            )

        return keyboard

    def _format_habits_message(self) -> str:
        l = localizator.localizator.lang(self._user_cache.language)
        
        text = ''
        text += f'📅 {l.habit_list_header} — {l.months[self._user_cache.last_datetime.month]} {self._user_cache.last_datetime.day}\n'
        text += f'{l.habit_list_tagline}\n'
        return text
