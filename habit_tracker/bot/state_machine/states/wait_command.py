from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from bot.states import HabitStates

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


class WaitCommand(IState):
    state = HabitStates.wait_command

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

    async def on_enter(self) -> None:
        # Отправить сообщение с кнопкой для создания привычки
        await super().on_enter()

    async def on_exit(self) -> None:
        # Удалить сообщение?
        await super().on_exit()
