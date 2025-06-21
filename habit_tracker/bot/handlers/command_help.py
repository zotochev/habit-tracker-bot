from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.cache import UserCache
from core import localizator

from bot.menu import MenuCommands


router = Router()


@router.message(Command(MenuCommands.help))
async def help_handler(message: Message, user_cache: UserCache):
    l = localizator.localizator.lang(user_cache.language)

    await message.answer(l.menu_help)

    await user_cache.state_machine.handle(message)
