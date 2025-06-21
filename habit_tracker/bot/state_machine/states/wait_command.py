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
        await message.delete()
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
        # l = localizator.localizator
        #
        # await setup_menu(self._user_cache.language, bot.bot_instance)
        #
        # await bot.bot_instance.send_message(
        #     chat_id=self._user_cache.telegram_id,
        #     text=l.lang(self._user_cache.language).create_habit,
        #     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        #         [
        #             InlineKeyboardButton(
        #                 text=l.lang(self._user_cache.language).button_create_habit,
        #                 callback_data=l.lang(self._user_cache.language).button_create_habit,
        #             )
        #         ]
        #     ])
        # )

    async def on_exit(self) -> None:
        # Удалить сообщение?
        await super().on_exit()
