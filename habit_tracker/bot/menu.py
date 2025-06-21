from enum import StrEnum, auto

from aiogram.types import BotCommand
from aiogram import Bot

from data.schemas.user import LanguageEnum
from core import localizator


class MenuCommands(StrEnum):
    add_habit = auto()
    list_habits = auto()
    help = auto()
    choose_langauge = auto()


async def setup_menu(language: LanguageEnum, bot: Bot) -> None:
    l = localizator.localizator

    commands = [
        BotCommand(command=MenuCommands.add_habit, description=l.lang(language).menu_add_habit),
        BotCommand(command=MenuCommands.list_habits, description=l.lang(language).menu_list_habits),
        BotCommand(command=MenuCommands.help, description=l.lang(language).menu_help),
        BotCommand(command=MenuCommands.choose_langauge, description=l.lang(language).choose_language),
    ]

    await bot.set_my_commands(commands)
