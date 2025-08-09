import logging

from data.factory import get_backend_repository

logger = logging.getLogger(__name__)


async def is_bot_ready_to_start() -> bool:
    repository = get_backend_repository()
    if not (await repository.health_check()):
        logger.error("Backend not responding on health check")
        return False

    return True
