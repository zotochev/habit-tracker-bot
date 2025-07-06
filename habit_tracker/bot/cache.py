from dataclasses import dataclass
from datetime import datetime

from bot.states import HabitStates
from bot.state_machine.state_machine import StateMachine
from bot.state_machine.states_factory import STATES_FACTORY
from data.schemas.user import LanguageEnum
from .messanger import Messenger


@dataclass
class UserCache:
    telegram_id: int
    language: LanguageEnum | None = None
    backend_id: int | None = None
    state_machine: StateMachine | None = None
    last_datetime: datetime | None = None
    messanger: Messenger | None = None


class Cache:
    def __init__(self):
        self.__users_cache: dict[int, UserCache] = {}

    def user(self, telegram_id: int):
        if telegram_id not in self.__users_cache:
            user_cache = UserCache(telegram_id=telegram_id)
            user_cache.state_machine = StateMachine(HabitStates.init, user_cache, STATES_FACTORY)
            user_cache.messanger = Messenger(telegram_id)
            self.__users_cache[telegram_id] = user_cache

        return self.__users_cache[telegram_id]

    def __contains__(self, telegram_id: int) -> bool:
        return telegram_id in self.__users_cache


cache: Cache | None = None


def setup_cache():
    global cache

    cache = Cache()
