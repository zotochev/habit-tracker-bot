from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data.factory import get_backend_repository
from data.repositories.backend_repository.backend_repository import BackendRepository
from bot.states import HabitStates
from data.schemas.user import LanguageEnum
import bot
from core import localizator
from bot.menu import setup_menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache


logger = logging.getLogger(__name__)


class IState(ABC):
    state: HabitStates = None

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 ) -> None:
        self._backend_repository = backend_repository
        self._user_cache = user_cache
        self._state_factory = state_factory

    async def handle(self, message: Message | CallbackQuery) -> IState:
        logger.warning(f"{self.__class__.__name__}: handle")
        if isinstance(message, Message):
            new_state = await self._handle_message(message)
        elif isinstance(message, CallbackQuery):
            new_state = await self._handle_callback_query(message)
        else:
            assert False, f"Unexpected message type: {type(message)}"

        return new_state

    @abstractmethod
    async def _handle_message(self, message: Message) -> IState:
        pass

    @abstractmethod
    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        pass

    async def on_enter(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_enter")

    async def on_exit(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_exit")

    def _create(self, state: HabitStates) -> IState:
        return self._state_factory[state](self._backend_repository, self._user_cache, self._state_factory)
