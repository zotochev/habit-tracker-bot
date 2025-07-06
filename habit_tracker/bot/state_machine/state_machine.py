from __future__ import annotations
import logging

from aiogram.types import Message, CallbackQuery

from data.factory import get_backend_repository
from bot.states import HabitStates
from .istate import IState
from .isuspendable_state import ISuspendableState

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
        self._suspended_states: list[ISuspendableState] = []

    async def handle(self, message: Message | CallbackQuery) -> None:
        new_state = await self._current_state.handle(message)

        if new_state is self._current_state:
            return

        if new_state.state == HabitStates.end:
            if self._suspended_states:
                new_state = self._suspended_states.pop()
                await new_state.on_restore()
                logger.warning(f"{self.__class__.__name__}: handle: restored {new_state.state}")
            else:
                new_state = self._create(HabitStates.help_command)
                await new_state.on_enter()
        else:
            await self._exit_or_suspend(self._current_state)
            await new_state.on_enter()

        self._current_state = new_state

    @property
    def state(self):
        return self._current_state.state

    async def set_state(self, state: HabitStates) -> None:
        if self._current_state.state == state:
            return

        new_state = await self._create_or_restore(state)
        await self._exit_or_suspend(self._current_state)
        self._current_state = new_state

        logger.warning(f"{self.__class__.__name__}: set_state: {state}")

    def _create(self, state: HabitStates) -> IState:
        assert state in self._states_factory, f'{self.__class__.__name__}._create({state}) -> state not found in factory {self._states_factory}'
        return self._states_factory[state](self._repository, self._user_cache, self._states_factory)

    async def _exit_or_suspend(self, state_instance: IState | ISuspendableState) -> None:
        if isinstance(self._current_state, ISuspendableState):
            logger.warning(f"{self.__class__.__name__}: _exit_or_suspend: {self._current_state} set on pause. Len of paused states: {len(self._suspended_states)}")
            self._suspended_states.append(self._current_state)
            paused_matched_states = [s for s in self._suspended_states if s.state == state_instance.state]
            assert len(paused_matched_states) in (0, 1), f"To many pause states: {paused_matched_states}"
            await state_instance.on_suspend()
        else:
            await state_instance.on_exit()

    async def _create_or_restore(self, state: HabitStates) -> IState:
        paused_matched_states = [s for s in self._suspended_states if s.state == state]
        assert len(paused_matched_states) in (0, 1), f"To many pause states: {paused_matched_states}"

        if paused_matched_states:
            state_instance = paused_matched_states[0]
            self._suspended_states = [s for s in self._suspended_states if s.state != state]
            await state_instance.on_restore()
        else:
            state_instance = self._create(state)
            await state_instance.on_enter()
        return state_instance
