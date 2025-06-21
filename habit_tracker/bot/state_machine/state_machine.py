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
from .istate import IState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.cache import UserCache


logger = logging.getLogger(__name__)


class StateMachine:
    def __init__(self, initial_state: HabitStates, user_cache: UserCache, states_factory: dict[HabitStates, IState.__class__]) -> None:
        self._repository = get_backend_repository()
        self._user_cache = user_cache
        self._states_factory = states_factory
        self._current_state = self._create(initial_state)
        self._paused_states = []

    async def handle(self, message: Message | CallbackQuery) -> None:
        new_state = await self._current_state.handle(message)

        if new_state is not self._current_state:
            await self._current_state.on_exit()
            await new_state.on_enter()

        if new_state.state == HabitStates.end:
            if self._paused_states:
                new_state = self._paused_states.pop()
            else:
                new_state = self._create(HabitStates.wait_command)

        self._current_state = new_state

    @property
    def state(self):
        return self._current_state.state

    def set_state(self, state: HabitStates) -> None:
        self._paused_states.append(self._current_state)
        self._current_state = self._create(state)

    def _create(self, state: HabitStates) -> IState:
        return self._states_factory[state](self._repository, self._user_cache, self._states_factory)
