from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from bot.states import HabitStates
from bot.state_machine.states_factory import register_state

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@register_state(HabitStates.end)
class EndState(IState):
    async def _handle_message(self, message: Message) -> IState:
        return await self._handle()

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        return await self._handle()

    async def _handle(self):
        return self
