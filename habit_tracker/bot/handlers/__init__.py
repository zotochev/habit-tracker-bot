from aiogram import Router

from .command_start import router as command_start_router
from .command_help import router as command_help_router
from .command_choose_language import router as command_choose_language
from .command_add_habit import router as command_add_habit
from .command_todays_habits import router as command_todays_habits
from .command_my_habits import router as command_my_habits

from .message import router as message_router
from .callback_query import router as callback_query_router


router = Router()

router.include_router(command_start_router)
router.include_router(command_help_router)
router.include_router(command_choose_language)
router.include_router(command_add_habit)
router.include_router(command_todays_habits)
router.include_router(command_my_habits)

router.include_router(message_router)
router.include_router(callback_query_router)
