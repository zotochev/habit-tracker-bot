import logging

import config

from data.factory import get_backend_repository

logger = logging.getLogger(__name__)


async def is_bot_ready_to_start() -> bool:
    repository = get_backend_repository()
    if not (await repository.health_check()):
        logger.error("Backend not responding on health check")
        return False

    return True


class InvalidSeed(Exception):
    pass


def add_seed_to_callback_data(data: str) -> str:
    return f"{config.SEED}:{data}"


def validate_seed_to_callback_data(data: str) -> str:
    seed_str, *d = data.split(":")

    if int(seed_str) != config.SEED:
        raise InvalidSeed(f"Button seed {seed_str} != {config.SEED}")

    return ":".join(d)
