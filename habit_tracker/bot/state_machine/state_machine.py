from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from data.factory import get_backend_repository
from bot.states import HabitStates
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
        self._paused_states: list[IState] = []

    async def handle(self, message: Message | CallbackQuery) -> None:
        new_state = await self._current_state.handle(message)

        if new_state is not self._current_state:
            await self._current_state.on_exit()
            await new_state.on_enter()

        if new_state.state == HabitStates.end:
            if self._paused_states:
                new_state = self._paused_states.pop()
                await new_state.on_restore()
                logger.warning(f"{self.__class__.__name__}: handle: restored {new_state.state}")
            else:
                new_state = self._create(HabitStates.wait_command)

        self._current_state = new_state

    @property
    def state(self):
        return self._current_state.state

    def set_state(self, state: HabitStates) -> None:
        self._paused_states.append(self._current_state)
        self._current_state = self._create(state)
        logger.warning(f"{self.__class__.__name__}: set_state: {state}")

    def _create(self, state: HabitStates) -> IState:
        assert state in self._states_factory, f'{self.__class__.__name__}._create({state}) -> state not found in factory'
        return self._states_factory[state](self._repository, self._user_cache, self._states_factory)
