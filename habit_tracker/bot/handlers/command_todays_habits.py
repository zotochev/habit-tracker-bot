from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.cache import UserCache
from bot.menu import MenuCommands
from bot.states import HabitStates


router = Router()


@router.message(Command(MenuCommands.todays_habits))
async def todays_habit_handler(message: Message, user_cache: UserCache):
    if user_cache.state_machine.state not in (HabitStates.command_todays_habits, HabitStates.todays_habits):
        await user_cache.state_machine.set_state(HabitStates.todays_habits)

    await user_cache.state_machine.handle(message)  # to update message
    await user_cache.messenger.remove_temp_messages()
