import config

from core.requester import Requester
from data.repositories.backend_repository.backend_repository import BackendRepository
from data.services.backend_service.backend_service import BackendService


def get_backend_repository() -> BackendRepository:
    requester = Requester(config.BACKEND_URL)
    service = BackendService(requester)
    repository = BackendRepository(service)
    return repository
