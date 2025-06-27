from enum import StrEnum, auto

from aiogram.types import BotCommand
from aiogram import Bot

from data.schemas.user import LanguageEnum
from core import localizator


class MenuCommands(StrEnum):
    add_habit = auto()
    todays_habits = auto()
    my_habits = auto()
    help = auto()
    choose_langauge = auto()
    progress = auto()


async def setup_menu(language: LanguageEnum, bot: Bot) -> None:
    l = localizator.localizator

    commands = [
        BotCommand(command=MenuCommands.todays_habits, description=l.lang(language).menu_list_habits),
        BotCommand(command=MenuCommands.my_habits, description=l.lang(language).menu_my_habits),
        BotCommand(command=MenuCommands.add_habit, description=l.lang(language).menu_add_habit),
        BotCommand(command=MenuCommands.choose_langauge, description=l.lang(language).menu_choose_language),
        BotCommand(command=MenuCommands.progress, description=l.lang(language).menu_progress),
        BotCommand(command=MenuCommands.help, description=l.lang(language).menu_help),
    ]

    await bot.set_my_commands(commands)
