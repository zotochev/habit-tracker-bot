from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.cache import UserCache
from bot.menu import MenuCommands
from bot.states import HabitStates


router = Router()


@router.message(Command(MenuCommands.choose_langauge))
async def choose_language_handler(message: Message, user_cache: UserCache):
    if user_cache.state_machine.state != HabitStates.choose_language:
        await user_cache.state_machine.set_state(HabitStates.choose_language)
    await user_cache.messenger.remove_temp_messages()
