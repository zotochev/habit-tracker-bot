from datetime import date, datetime

from data.services.backend_service.backend_service import BackendService
from data.schemas import (
    User,
    Habit,
    HabitBuffer,
    HabitEvent,
    HabitUpdate,
    CommonProgress,
    UserUpdate,
    HabitProgress,
    HabitStatistics,
    Notification, NotificationBase,
)


class BackendRepository:
    def __init__(self, backend_service: BackendService) -> None:
        self._service = backend_service

    async def get_user_info(self, telegram_id: int) -> User | None:
        return await self._service.get_user_by_telegram(telegram_id)

    async def get_user(self, user_id: int) -> User | None:
        return await self._service.get_user(user_id)

    async def register_user_by_telegram(self, user_name: str, telegram_id: int) -> User | None:
        return await self._service.register_user_by_telegram(user_name, telegram_id)

    async def update_user(self, user: UserUpdate) -> User | None:
        return await self._service.update_user(user)

    async def get_habit_by_user_id_and_name(self, user_id: int, habit_name: str) -> Habit | None:
        return await self._service.get_habit_by_user_id_and_name(user_id, habit_name)

    async def create_habit(self, user_id: int, habit_buffer: HabitBuffer) -> Habit | None:
        return await self._service.create_habit(user_id, habit_buffer)

    async def get_habits_for_date(self, user_id: int, habit_date: date, unfinished_only: bool = False) -> list[HabitProgress] | None:
        return await self._service.get_habits_for_date(user_id, habit_date, unfinished_only)

    async def send_habit_event(self, notification_id: int, timestamp: datetime) -> HabitEvent:
        return await self._service.send_habit_event(notification_id, timestamp)

    async def get_habit_by_user_id_and_id(self, user_id: int, habit_id: int) -> Habit | None:
        return await self._service.get_habit_by_user_id_and_id(user_id, habit_id)

    async def update_habit(self, habit: HabitUpdate, notifications: list[NotificationBase] | None = None) -> Habit | None:
        return await self._service.update_habit(habit, notifications)

    async def get_habit_statistics(self, user_id: int, habit_id: int, target_date: date) -> HabitStatistics:
        return await self._service.get_habit_statistics(user_id, habit_id, target_date)

    async def get_all_habits_statistics(self, user_id: int, today: date) -> CommonProgress | None:
        return await self._service.get_all_habits_statistics(user_id, today)

    async def delete_habit(self, user_id: int, habit_id: int) -> None:
        return await self._service.delete_habit(user_id, habit_id)

    async def get_notifications_for_period(self, now: datetime, period: int) -> list[Notification]:
        return await self._service.get_notifications_for_period(now, period)

    async def get_todays_notifications(self, user_id: int, today: date) -> list[Notification] | None:
        return await self._service.get_todays_notifications(user_id, today)
    
    async def get_habit_notifications(self, habit_id: int) -> list[Notification] | None:
        return await self._service.get_habit_notifications(habit_id)

    async def create_notification(self, habit_id: int, time_in_seconds: int | None = None) -> Notification | None:
        return await self._service.create_notification(habit_id, time_in_seconds)

    async def health_check(self) -> bool:
        return await self._service.health_check()
