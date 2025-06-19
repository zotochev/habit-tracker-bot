from aiogram import Router

from .start import router as start_router
from .create_habit import router as default_router


router = Router()

router.include_router(start_router)
router.include_router(default_router)
