from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.state_machine.states_factory import register_state

from bot.state_machine.istate import IState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


logger = logging.getLogger(__name__)


@register_state(HabitStates.choose_language)
class ChooseLanguage(IState):

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory)
        self._message_with_button = None

    async def _handle_message(self, message: Message) -> IState:
        message_text = message.text
        result = await self._handle(message_text)
        await message.delete()
        return result

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        message_text = callback_query.data
        result = await self._handle(message_text)

        l = localizator.localizator
        await callback_query.answer(l.lang(self._user_cache.language).language_chosen)

        return result

    async def _handle(self, message_text: str) -> IState:
        try:
            language = LanguageEnum(message_text)
        except Exception as e:
            print(f"Not a valid language: {message_text}")
            return self

        self._user_cache.language = language
        user = await self._backend_repository.update_user_language(
            self._user_cache.backend_id,
            self._user_cache.language,
        )
        assert user, f"Failed to assign language {self._user_cache.backend_id}:{self._user_cache.telegram_id} -> {language}"
        return self._create(HabitStates.end)

    async def on_enter(self) -> None:
        await super().on_enter()
        l = localizator.localizator

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=icon, callback_data=language)
                for language, icon in LanguageEnum.map().items()
            ]
        ])
        text = '\n'.join(l.lang(lang).menu_choose_language for lang in LanguageEnum.all())

        self._message_with_button = await bot.bot_instance.send_message(
            chat_id=self._user_cache.telegram_id,
            text=text,
            reply_markup=keyboard,
        )

    async def on_exit(self) -> None:
        await super().on_exit()
        if self._message_with_button is not None:
            try:
                await self._message_with_button.delete()
            except Exception as e:
                logger.warning(f"{self.__class__.__name__}.on_exit: {e.__class__.__name__}: {e}")


