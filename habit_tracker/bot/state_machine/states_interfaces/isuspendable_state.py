import logging
from .istatable import IStatable


logger = logging.getLogger(__name__)


class ISuspendableState(IStatable):
    async def on_restore(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_restore")

    async def on_suspend(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_suspend")
