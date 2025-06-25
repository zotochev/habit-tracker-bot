import logging


logger = logging.getLogger(__file__)


class ISuspendableState:
    async def on_restore(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_restore")

    async def on_suspend(self) -> None:
        logger.warning(f"{self.__class__.__name__}: on_suspend")
