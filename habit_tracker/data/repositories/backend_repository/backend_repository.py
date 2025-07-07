from datetime import date

from data.schemas.habit_event import HabitStatistics
from data.services.backend_service.backend_service import BackendService
from data.schemas import (
    User,
    Habit,
    HabitBuffer,
    HabitEvent,
    HabitUpdate,
    CommonProgress,
)


class BackendRepository:
    def __init__(self, backend_service: BackendService) -> None:
        self._service = backend_service

    async def get_user_info(self, telegram_id: int) -> User | None:
        return await self._service.get_user_by_telegram(telegram_id)

    async def register_user_by_telegram(self, user_name: str, telegram_id: int) -> User | None:
        return await self._service.register_user_by_telegram(user_name, telegram_id)

    async def update_user_language(self, backend_user_id: int, language: str) -> User | None:
        return await self._service.update_user_language(backend_user_id, language)

    async def get_habit_by_user_id_and_name(self, user_id: int, habit_name: str) -> Habit | None:
        return await self._service.get_habit_by_user_id_and_name(user_id, habit_name)

    async def create_habit(self, user_id: int, habit_buffer: HabitBuffer) -> Habit | None:
        return await self._service.create_habit(user_id, habit_buffer)

    async def get_habits_for_date(self, user_id: int, habit_date: date, unfinished_only: bool = False) -> Habit | None:
        return await self._service.get_habits_for_date(user_id, habit_date, unfinished_only)

    async def send_habit_event(self, habit_id: int, timestamp: date) -> HabitEvent:
        return await self._service.send_habit_event(habit_id, timestamp)

    async def get_habit_by_user_id_and_id(self, user_id: int, habit_id: int) -> HabitUpdate | None:
        return await self._service.get_habit_by_user_id_and_id(user_id, habit_id)

    async def update_habit(self, habit: HabitUpdate) -> Habit | None:
        return await self._service.update_habit(habit)

    async def get_habit_statistics(self, user_id: int, habit_id: int, target_date: date) -> HabitStatistics:
        return await self._service.get_habit_statistics(user_id, habit_id, target_date)

    async def get_all_habits_statistics(self, user_id: int, today: date) -> CommonProgress | None:
        return await self._service.get_all_habits_statistics(user_id, today)
