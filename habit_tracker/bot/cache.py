from dataclasses import dataclass, field
from bot.states import HabitStates
from data.schemas import HabitBuffer
from bot.state_machine.state_machine import StateMachine
from bot.state_machine.states_factory import STATES_FACTORY
from data.schemas.user import LanguageEnum


@dataclass
class UserCache:
    telegram_id: int
    language: LanguageEnum | None = None
    habit: HabitBuffer = field(default_factory=HabitBuffer)
    backend_id: int | None = None
    temp_message_id: int | None = None
    state_machine: StateMachine | None = None


class Cache:
    def __init__(self):
        self.__users_cache: dict[int, UserCache] = {}

    def user(self, telegram_id: int):
        if telegram_id not in self.__users_cache:
            user_cache = UserCache(telegram_id=telegram_id)
            user_cache.state_machine = StateMachine(HabitStates.init, user_cache, STATES_FACTORY)
            self.__users_cache[telegram_id] = user_cache

        return self.__users_cache[telegram_id]

    def __contains__(self, telegram_id: int) -> bool:
        return telegram_id in self.__users_cache


cache: Cache | None = None


def setup_cache():
    global cache

    cache = Cache()
