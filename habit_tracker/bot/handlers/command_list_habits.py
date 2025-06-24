from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.cache import UserCache
from bot.menu import MenuCommands
from bot.states import HabitStates

router = Router()


@router.message(Command(MenuCommands.todays_habits))
async def list_habit_handler(message: Message, user_cache: UserCache):
    if user_cache.state_machine.state not in (HabitStates.command_list_habits, HabitStates.list_habits):
        user_cache.state_machine.set_state(HabitStates.command_list_habits)
        await message.delete()
    await user_cache.state_machine.handle(message)
