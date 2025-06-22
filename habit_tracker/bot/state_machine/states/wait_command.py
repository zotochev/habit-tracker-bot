from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


@register_state(HabitStates.wait_command)
class WaitCommand(IState):

    async def _handle_message(self, message: Message) -> IState:
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"{self.__class__.__name__}._handle_message: {e.__class__.__name__}: {e}")
        return self

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        message_text = callback_query.data
        await callback_query.answer()
        return await self._handle(message_text)

    async def _handle(self, message_text: str) -> IState:
        return self
