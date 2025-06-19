from dataclasses import dataclass, field
from bot.states import HabitStates
from data.schemas import HabitBuffer
from aiogram.types import Message


@dataclass
class UserCache:
    telegram_id: int
    language: str = 'ru'
    state: HabitStates = HabitStates.init
    habit: HabitBuffer = field(default_factory=HabitBuffer)
    temp_message_id: int | None = None


class Cache:
    def __init__(self):
        self.__users_cache: dict[int, UserCache] = {}

    def user(self, telegram_id: int):
        if telegram_id not in self.__users_cache:
            self.__users_cache[telegram_id] = UserCache(telegram_id=telegram_id)

        return self.__users_cache[telegram_id]

    def __contains__(self, telegram_id: int) -> bool:
        return telegram_id in self.__users_cache


cache: Cache | None = None


def setup_cache():
    global cache

    cache = Cache()
