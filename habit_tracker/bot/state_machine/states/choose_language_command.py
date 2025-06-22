from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.menu import setup_menu
from bot.state_machine.states_factory import register_state

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@register_state(HabitStates.command_choose_language)
class ChooseLanguageCommand(IState):

    async def _handle_message(self, message: Message) -> IState:
        message_text = message.text
        result = await self._handle(message_text)
        await message.delete()
        return result

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        result = self

        l = localizator.localizator
        await callback_query.answer(l.lang(self._user_cache.language).unexpected)

        await callback_query.message.delete()

        return result

    async def _handle(self, message_text: str) -> IState:
        return self._create(HabitStates.choose_language)

    async def on_enter(self) -> None:
        await super().on_enter()
        l = localizator.localizator

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=icon, callback_data=language)
                for language, icon in LanguageEnum.map().items()
            ]
        ])
        text = '\n'.join(l.lang(lang).choose_language for lang in LanguageEnum.all())

        await bot.bot_instance.send_message(
            chat_id=self._user_cache.telegram_id,
            text=text,
            reply_markup=keyboard,
        )

    async def on_exit(self) -> None:
        await super().on_exit()
