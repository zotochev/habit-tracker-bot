from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot import cache
from bot.states import HabitStates


class HabitStateFilter(BaseFilter):
    def __init__(self, habit_state: HabitStates) -> None:
        self._habit_state = habit_state

    async def __call__(self, message: Message) -> bool:
        user_cache = cache.cache.user(message.from_user.id)
        return user_cache.state_machine.state == self._habit_state
