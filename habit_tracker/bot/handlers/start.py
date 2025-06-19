from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from core import localizator

from data.schemas.user import LanguageEnum
from bot.cache import UserCache
from bot.states import HabitStates
from bot.filters import HabitStateFilter


router = Router()


language_keyboards = {
    "🇷🇺": "ru",
    "🇬🇧": "en",
}
language_keyboards_values = list(language_keyboards.values())


keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=k, callback_data=v)
        for k, v in language_keyboards.items()
    ]
])


def create_habit_markup(text, callback_data):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=text, callback_data=callback_data)
        ]
    ])


@router.message(Command('start'))
async def start(message: Message, user_cache: UserCache):
    message_text = '\n'.join([
        localizator.localizator.lang(x).choose_language
        for x in LanguageEnum.ALL()
    ])

    await message.answer(
        message_text,
        reply_markup=keyboard,
    )


@router.callback_query(HabitStateFilter(HabitStates.init), lambda c: c.data in list(language_keyboards.values()))
async def set_language(callback_query: CallbackQuery, user_cache: UserCache):
    user_cache.language = LanguageEnum(callback_query.data)
    user_cache.state = HabitStates.wait_start_enter_habit
    l = localizator.localizator

    await callback_query.answer(
        l.lang(user_cache.language).language_chosen,
    )
    await callback_query.message.answer(
        l.lang(user_cache.language).create_habit,
        reply_markup=create_habit_markup(
            text=l.lang(user_cache.language).button_create_habit,
            callback_data=l.lang(user_cache.language).button_create_habit,
        )
    )
    await callback_query.message.delete()


@router.callback_query(lambda c: c.data in list(language_keyboards.values()))
async def set_language_not_init(callback_query: CallbackQuery, user_cache: UserCache):
    user_cache.language = LanguageEnum(callback_query.data)
    user_cache.state = HabitStates.wait_start_enter_habit
    l = localizator.localizator

    await callback_query.answer(
        l.lang(user_cache.language).language_chosen,
    )
    await callback_query.message.delete()
