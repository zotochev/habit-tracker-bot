from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from aiogram.types import Message, CallbackQuery

from bot.states import HabitStates

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


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
        if isinstance(message, Message):
            text = self.__trim_text(message.text)
            logger.warning(f"{self.__class__.__name__}: handle: {text}")
            new_state = await self._handle_message(message)
        elif isinstance(message, CallbackQuery):
            text = self.__trim_text(message.message.text)
            logger.warning(f"{self.__class__.__name__}: handle: {text}")
            new_state = await self._handle_callback_query(message)
        else:
            assert False, f"Unexpected message type: {type(message)}"

        return new_state

    @staticmethod
    def __trim_text(text: str) -> str:
        line_feed_index = text.find('\n')
        end_index = line_feed_index if line_feed_index > 0 else None
        return text[:end_index]

    async def on_enter(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_enter")

    async def on_exit(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_exit")

    @abstractmethod
    async def _handle_message(self, message: Message) -> IState:
        pass

    @abstractmethod
    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        pass

    def _create(self, state: HabitStates, **kwargs) -> IState:
        assert state in self._state_factory, f'{self.__class__.__name__}._create({state}) -> state not found in factory'
        return self._state_factory[state](self._backend_repository, self._user_cache, self._state_factory, **kwargs)
