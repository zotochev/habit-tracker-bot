from datetime import date, datetime

from fastapi.encoders import jsonable_encoder

from core.requester import Requester, Response
from data.schemas import (
    UserUpdate,
    User,
    TelegramAccount,
    Habit,
    HabitBuffer,
    HabitCreate,
    HabitEvent,
    HabitUpdate,
    HabitNotification,
    HabitStatistics,
    CommonProgress,
)
from data.schemas.habit import HabitProgress


class BackendService:
    def __init__(self, requester: Requester) -> None:
        self._requester: Requester = requester

    async def register_user_by_telegram(self, user_name: str, telegram_id: int) -> User | None:
        r: Response = await self._requester.post(
            "v1/auth/signup-telegram",
            body={'name': user_name, 'telegram_id': telegram_id},
        )

        if not r.ok():
            return

        return User(**r.body)

    async def get_user(self, user_id: int) -> User | None:
        r: Response = await self._requester.get(
            "v1/users",
            query={'user_id': user_id},
        )

        if not r.ok():
            return

        return User(**r.body)

    async def update_user(self, user: UserUpdate) -> User | None:
        r: Response = await self._requester.patch(
            "v1/users",
            body=user.model_dump(exclude_none=True),
        )

        if not r.ok():
            return

        return User(**r.body)

    async def get_user_by_telegram(self, telegram_id: int) -> User | None:
        r: Response = await self._requester.get("v1/users/telegram", query={'telegram_id': telegram_id})

        if not r.ok():
            return

        return User(**r.body)

    async def get_habit_by_user_id_and_name(self, user_id: int, habit_name: str) -> Habit | None:
        r: Response = await self._requester.get("v1/habits/habit", query={'user_id': user_id, 'habit_name': habit_name})

        if not r.ok():
            return

        return Habit(**r.body)

    async def create_habit(self, user_id: int, habit_buffer: HabitBuffer) -> Habit | None:
        habit = HabitCreate(user_id=user_id, **habit_buffer.model_dump())
        r: Response = await self._requester.post("v1/habits", body=jsonable_encoder(habit.model_dump()))

        if not r.ok():
            return

        return Habit(**r.body)

    async def get_habits_for_date(self, user_id: int, habit_date: date, unfinished_only: bool = False) -> list[HabitProgress] | None:
        r: Response = await self._requester.get(
            "v1/habits/event/progress",
            query=jsonable_encoder({'user_id': user_id, 'habit_date': habit_date, 'unfinished_only': int(unfinished_only)}),
        )

        if not r.ok():
            return

        return [HabitProgress(**h) for h in r.body]

    async def send_habit_event(self, habit_id: int, timestamp: date) -> HabitEvent | None:
        r: Response = await self._requester.post(f"v1/habits/{habit_id}/event", body=jsonable_encoder({'timestamp': timestamp}))

        if not r.ok():
            return

        return HabitEvent(**r.body)

    async def get_habit_by_user_id_and_id(self, user_id: int, habit_id: int) -> HabitUpdate | None:
        r: Response = await self._requester.get(f"v1/habits/{habit_id}", query={'user_id': user_id})

        if not r.ok():
            return

        return HabitUpdate(**r.body)

    async def update_habit(self, habit: HabitUpdate) -> HabitUpdate | None:
        r: Response = await self._requester.patch(f"v1/habits/", body=jsonable_encoder(habit.model_dump()))

        if not r.ok():
            return

        return HabitUpdate(**r.body)

    async def get_habit_statistics(self, user_id: int, habit_id: int, target_date: date) -> HabitStatistics | None:
        r: Response = await self._requester.get(
            f"v1/habits/event/statistics",
            query=jsonable_encoder(
                {'user_id': user_id, 'habit_id': habit_id, 'today': target_date},
            ),
        )

        if not r.ok():
            return

        return HabitStatistics(**r.body)

    async def get_all_habits_statistics(self, user_id: int, today: date) -> CommonProgress | None:
        r: Response = await self._requester.get(
            f"v1/habits/event/statistics/all",
            query=jsonable_encoder(
                {'user_id': user_id, 'today': today},
            ),
        )

        if not r.ok():
            return

        return CommonProgress(**r.body)

    async def delete_habit(self, user_id: int, habit_id: int) -> None:
        r: Response = await self._requester.delete(f"v1/habits/{habit_id}", query={'user_id': user_id})

        if not r.ok():
            return

        return

    async def get_notifications_for_period(self, now: datetime, period: int) -> list[HabitNotification] | None:
        r: Response = await self._requester.get(
            f"v1/habits/notifications/all",
            query=jsonable_encoder({'now': now, 'period': period}),
        )

        if not r.ok():
            return

        return [HabitNotification(**h) for h in r.body]
