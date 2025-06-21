from fastapi.encoders import jsonable_encoder

from core.requester import Requester, Response
from data.schemas import UserUpdate, User, TelegramAccount, Habit, HabitBuffer, HabitCreate


class BackendService:
    def __init__(self, requester: Requester) -> None:
        self._requester: Requester = requester

    async def register_user_by_telegram(self, user_name: str, telegram_id: int) -> TelegramAccount | None:
        r: Response = await self._requester.post(
            "v1/auth/signup-telegram",
            body={'name': user_name, 'telegram_id': telegram_id},
        )

        if not r.ok():
            return

        return TelegramAccount(**r.body)

    async def update_user_language(self, backend_user_id: int, language: str) -> UserUpdate | None:
        r: Response = await self._requester.patch(
            "v1/users",
            body={'language': language, 'id': backend_user_id},
        )

        if not r.ok():
            return

        return UserUpdate(**r.body)

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
