from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import HabitStates
from bot.state_machine.states_factory import register_state
from bot.state_machine.states_interfaces import IState, ISuspendableState

from core import localizator

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.settings)
class SettingsState(IState, ISuspendableState):
    BACK_BUTTON = "settings_back_button"

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 **kwargs,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory, **kwargs)

    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        await callback_query.answer()

        if callback_query.data == self.BACK_BUTTON:
            return self._create(HabitStates.end)

        return self._create(HabitStates(int(callback_query.data)))

    async def _handle(self):
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        l = localizator.localizator.lang(self._user_cache.language)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for callback_data, text in (
            (HabitStates.choose_language, l.menu_choose_language),
            (HabitStates.choose_timezone, l.menu_choose_timezone),
        ):
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=text,
                        callback_data=str(callback_data.value),
                    ),
                ]
            )

        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=l.button_back,
                    callback_data=self.BACK_BUTTON,
                ),
            ]
        )
        await self._user_cache.messenger.update_main_message(l.menu_settings, keyboard)

    async def on_restore(self) -> None:
        await super().on_restore()
        await self.on_enter()
