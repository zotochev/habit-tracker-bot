from __future__ import annotations

import logging
import asyncio
import datetime

from bot import cache
from core import localizator
from data.factory import get_backend_repository

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import UserCache
    from bot.messenger_queue import MessengerQueue
    from data.repositories.backend_repository.backend_repository import BackendRepository
    from data.schemas.notification import Notification


UserId = int
HabitId = int
# Dedup key: (user_id, habit_id, notification_id or -1, time_in_seconds or -1)
SendNotificationsKey = tuple[int, int, int, int]

logger = logging.getLogger(__name__)


class Notificator:
    PERIOD_SECONDS = 10
    PERIOD_OVERLAP = 2

    def __init__(self, message_queue: MessengerQueue, backend_repository: BackendRepository):
        self.__messenger_queue = message_queue
        self.__backend_repository = backend_repository
        self.__should_stop = False
        self.__previously_sent_notifications: set[SendNotificationsKey] = set()
        self.__telegram_id_by_user_id: dict[int, int] = {}
        self.__habit_name_by_id: dict[int, str] = {}

    async def process_notifications(self) -> None:
        while not self.__should_stop:
            now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=self.PERIOD_OVERLAP)
            notifications: list[Notification] | None = None

            try:
                notifications = await self.__backend_repository.get_notifications_for_period(
                    now, self.PERIOD_SECONDS + self.PERIOD_OVERLAP,
                )
            except Exception as e:
                logger.error(f"Failed to retrieve notifications for {now}: {e.__class__.__name__}:{e}")

            if notifications is not None:
                not_sent_notifications: list[Notification] = []

                for n in notifications:
                    user_id = getattr(n, 'user_id', None)
                    if user_id is None:
                        # Cannot route without user_id; skip with error
                        logger.error(f"Notification {n.notification_id} missing user_id; skipping")
                        continue
                    key: SendNotificationsKey = (
                        int(user_id),
                        int(n.habit_id),
                        int(n.notification_id) if n.notification_id is not None else -1,
                        int(n.time_in_seconds) if n.time_in_seconds is not None else -1,
                    )
                    if key not in self.__previously_sent_notifications:
                        not_sent_notifications.append(n)

                self.__previously_sent_notifications.clear()

                for n in not_sent_notifications:
                    user_id = n.user_id
                    if user_id is None:
                        continue
                    key: SendNotificationsKey = (
                        int(user_id),
                        int(n.habit_id),
                        int(n.notification_id) if n.notification_id is not None else -1,
                        int(n.time_in_seconds) if n.time_in_seconds is not None else -1,
                    )

                    try:
                        # Resolve telegram id
                        if user_id in self.__telegram_id_by_user_id:
                            telegram_id = self.__telegram_id_by_user_id[user_id]
                        else:
                            user = await self.__backend_repository.get_user(user_id)
                            telegram_id = user.telegram_account.telegram_id
                            assert telegram_id is not None
                            self.__telegram_id_by_user_id[user_id] = telegram_id

                        user_cache = cache.cache.user(telegram_id)
                        if not user_cache.is_inited:
                            await cache.cache.setup_user(telegram_id)

                        # Resolve habit name
                        habit_name = n.habit_name
                        if not habit_name:
                            if n.habit_id in self.__habit_name_by_id:
                                habit_name = self.__habit_name_by_id[n.habit_id]
                            else:
                                habit = await self.__backend_repository.get_habit_by_user_id_and_id(user_id, n.habit_id)
                                habit_name = habit.name
                                self.__habit_name_by_id[n.habit_id] = habit_name

                        messenger = self.__messenger_queue.get_messenger(telegram_id)

                        await messenger.send_message(
                            self.__generate_message(user_cache, habit_name, n)
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
    def __generate_message(user_cache: UserCache, habit_name: str, notification: Notification) -> str:
        l = localizator.localizator.lang(user_cache.language)

        # Format time according to user's timezone if available
        local_time_str = '-'
        if notification.time_in_seconds is not None:
            t = notification.time(user_cache.timezone)
            local_time_str = f"{t.hour:02}:{t.minute:02}"
        return l.notification.format(
            time=local_time_str,
            name=habit_name,
        )


def setup_notificator(message_queue: MessengerQueue) -> Notificator:
    return Notificator(message_queue, get_backend_repository())
