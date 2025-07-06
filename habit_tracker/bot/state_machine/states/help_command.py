from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from bot.state_machine.istate import IState

from core import localizator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


@register_state(HabitStates.help_command)
class HelpCommand(IState):
    async def _handle_message(self, message: Message) -> IState:
        return await self._handle(message.text)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        message_text = callback_query.data
        await callback_query.answer()
        return await self._handle(message_text)

    async def _handle(self, message_text: str) -> IState:
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        l = localizator.localizator.lang(self._user_cache.language)
        await self._user_cache.messanger.update_main_message(l.menu_help)
