from __future__ import annotations

import logging
import asyncio
import datetime

from bot import cache
from core.timezone_utils import utc_to_local
from core import localizator
from data.factory import get_backend_repository

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from bot.messenger_queue import MessengerQueue
    from data.repositories.backend_repository.backend_repository import BackendRepository


UserId = int
HabitId = int
SendNotificationsKey = tuple[UserId, HabitId, datetime.time]

logger = logging.getLogger(__name__)


class Notificator:
    PERIOD_SECONDS = 10
    PERIOD_OVERLAP = 2

    def __init__(self, message_queue: MessengerQueue, backend_repository: BackendRepository):
        self.__messenger_queue = message_queue
        self.__backend_repository = backend_repository
        self.__should_stop = False
        self.__previously_sent_notifications: set[SendNotificationsKey] = set()
        self.__telegram_id_by_user_id = {}

    async def process_notifications(self) -> None:
        # tasks = []

        while not self.__should_stop:
            now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=self.PERIOD_OVERLAP)
            habits = None

            try:
                habits = await self.__backend_repository.get_notifications_for_period(
                    now, self.PERIOD_SECONDS + self.PERIOD_OVERLAP,
                )
            except Exception as e:
                logger.error(f"Failed to retrieve habits with notifications for {now}: {e.__class__.__name__}:{e}")

            if habits is not None:
                not_sent_habits = []

                for habit in habits:
                    for notification in habit.notifications:
                        key = (habit.user_id, habit.id, notification)
                        if key not in self.__previously_sent_notifications:
                            not_sent_habits.append(habit)

                self.__previously_sent_notifications.clear()

                for habit in not_sent_habits:
                    for notification in habit.notifications:
                        key = (habit.user_id, habit.id, notification)

                        try:
                            if habit.user_id in self.__telegram_id_by_user_id:
                                telegram_id = self.__telegram_id_by_user_id[habit.user_id]
                            else:
                                user = await self.__backend_repository.get_user(habit.user_id)
                                telegram_id = user.telegram_account.telegram_id
                                assert telegram_id is not None
                                self.__telegram_id_by_user_id[habit.user_id] = telegram_id

                            user_cache = cache.cache.user(telegram_id)
                            if not user_cache.is_inited:
                                await cache.cache.setup_user(telegram_id)

                            messenger = self.__messenger_queue.get_messenger(telegram_id)

                            await messenger.send_message(
                                self.__generate_message(user_cache, habit.name, notification)
                            )
                        except Exception as e:
                            logger.exception(e)
                        self.__previously_sent_notifications.add(key)
            else:
                logger.error(f"Notificator: failed to get notifications for {now}")

            await asyncio.sleep(self.PERIOD_SECONDS)

    def stop(self) -> None:
        self.__should_stop = True

    @staticmethod
    def __generate_message(user_cache: UserCache, habit_name: str, notification_time: datetime.time) -> str:
        l = localizator.localizator.lang(user_cache.language)

        local_time = utc_to_local(notification_time, user_cache.timezone)
        return l.notification.format(
            time=local_time.strftime("%H:%M"),
            name=habit_name,
        )


def setup_notificator(message_queue: MessengerQueue) -> Notificator:
    return Notificator(message_queue, get_backend_repository())
