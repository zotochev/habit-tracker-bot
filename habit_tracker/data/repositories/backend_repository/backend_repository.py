from data.services.backend_service.backend_service import BackendService
from data.schemas import User


class BackendRepository:
    def __init__(self, backend_service: BackendService) -> None:
        self._service = backend_service

    async def get_user_info(self, telegram_id: int) -> User | None:
        return await self._service.get_user_by_telegram(telegram_id)

    async def register_user_by_telegram(self, user_name: str, telegram_id: int) -> User | None:
        return await self._service.register_user_by_telegram(user_name, telegram_id)

    async def update_user_language(self, backend_user_id: int, language: str) -> User | None:
        return await self._service.update_user_language(backend_user_id, language)
