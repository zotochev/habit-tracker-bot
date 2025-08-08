import logging
from abc import abstractmethod, ABC


logger = logging.getLogger(__name__)


class IContextTypeHandable(ABC):
    @abstractmethod
    def is_handable(self, context_type) -> bool:
        pass
