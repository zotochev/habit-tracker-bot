from __future__ import annotations
import asyncio
import logging
from collections import deque
from collections.abc import Callable, Coroutine

from bot.messanger import Messenger


logger = logging.getLogger(__file__)


class MessangerQueue:
    MAX_MESSAGES_TOTAL = 30
    MAX_MESSAGES_PER_USER = 1
    PERIOD_SECONDS = 1
    instance: MessangerQueue | None = None

    def __init__(self):
        self.__messangers = {}
        self.__messangers_queue = deque()
        self.__should_stop = False

    def get_messanger(self, telegram_id: int) -> Messenger:
        if telegram_id not in self.__messangers:
            self.__messangers[telegram_id] = Messenger(telegram_id)
            self.__messangers_queue.append(self.__messangers[telegram_id])
        return self.__messangers[telegram_id]

    async def process_messages(self) -> None:
        tasks = []

        while not self.__should_stop:
            for _ in range(min(len(self.__messangers_queue), self.MAX_MESSAGES_TOTAL)):
                messenger = self.__messangers_queue.pop()
                tasks.append(
                    self.__wrap_task_in_except(messenger.process_message)
                )
                self.__messangers_queue.appendleft(messenger)

            await asyncio.gather(*tasks)
            tasks.clear()
            await asyncio.sleep(self.PERIOD_SECONDS)

    def stop(self) -> None:
        self.__should_stop = True

    async def __wrap_task_in_except(self, task: Callable[[], Coroutine]) -> None:
        try:
            await task()
        except Exception as e:
            logger.exception(e)
            logger.error(f'{self.__class__.__name__}.process_message() -> {e.__class__.__name__}:{e}')


def setup_messanger_queue() -> MessangerQueue:
    messanger_queue = MessangerQueue()
    MessangerQueue.instance = messanger_queue
    return messanger_queue
