from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from bot.states import HabitStates
from bot.state_machine.state_machine import StateMachine
from bot.state_machine.states_factory import STATES_FACTORY
from data.factory import get_backend_repository
from data.schemas.user import LanguageEnum
from .messenger import Messenger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .messenger_queue import MessengerQueue


logger = logging.getLogger(__name__)


@dataclass
class UserCache:
    telegram_id: int
    language: LanguageEnum | None = None
    timezone: str | None = None
    backend_id: int | None = None
    state_machine: StateMachine | None = None
    last_datetime: datetime | None = None
    messenger: Messenger | None = None
    is_inited: bool = False

    def is_registered(self) -> bool:
        return self.backend_id is not None


class Cache:
    def __init__(self, messenger_queue: MessengerQueue):
        self.__users_cache: dict[int, UserCache] = {}
        self.__messenger_queue = messenger_queue

    def user(self, telegram_id: int):
        if telegram_id not in self.__users_cache:
            user_cache = UserCache(telegram_id=telegram_id)
            user_cache.state_machine = StateMachine(HabitStates.init, user_cache, STATES_FACTORY)
            user_cache.messenger = self.__messenger_queue.get_messenger(telegram_id)
            self.__users_cache[telegram_id] = user_cache

        return self.__users_cache[telegram_id]

    def __contains__(self, telegram_id: int) -> bool:
        return telegram_id in self.__users_cache

    async def setup_user(self, telegram_id: int) -> UserCache:
        repository = get_backend_repository()

        if telegram_id not in self.__users_cache:
            user_cache = UserCache(telegram_id=telegram_id)
            user_cache.state_machine = StateMachine(HabitStates.init, user_cache, STATES_FACTORY)
            user_cache.messenger = self.__messenger_queue.get_messenger(telegram_id)
        else:
            user_cache = self.__users_cache[telegram_id]

        user = await repository.get_user_info(telegram_id)
        if user is not None:
            user_cache.backend_id = user.id
            user_cache.language = user.language
            user_cache.timezone = user.timezone
        else:
            logger.error(f"{self.__class__.__name__}: setup_user: failed to retrive info for user {telegram_id=}")

        return user_cache


cache: Cache | None = None


def setup_cache(messenger_queue: MessengerQueue):
    global cache

    cache = Cache(messenger_queue)
