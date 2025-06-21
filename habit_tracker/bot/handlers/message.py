from aiogram import Router
from aiogram.types import (
    Message,
    ContentType,
)

from bot.state_machine.states.wait_command import logger
from bot.cache import UserCache
from core import localizator


router = Router()


def is_valid_habit_name(name: str, max_words: int = 3, max_length: int = 30) -> bool:
    if not name or len(name) > max_length:
        return False

    words = name.split()
    return 1 <= len(words) <= max_words


def is_command_message(message: Message) -> bool:
    if message.text is None:
        return False
    entities = message.entities or []
    # any(e.type == "bot_command" for e in message.entities)
    #  and e.offset == 0
    return any(e.type == "bot_command" for e in entities)


@router.message(lambda message: not is_command_message(message))
async def habit_name(message: Message, user_cache: UserCache):
    logger.warning(f"MESSAGE: {message.text}")
    # HabitStateFilter(HabitStates.enter_habit_name)
    l = localizator.localizator.lang(user_cache.language)

    if message.content_type != ContentType.TEXT:
        await message.answer(l.wrong_type_habit_name)
        return

    if not is_valid_habit_name(message.text, max_words=999, max_length=300):
        await message.answer(l.habit_name_too_long)
        return

    await user_cache.state_machine.handle(message)


# def create_date_keyboard():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="^", callback_data=f"up_day"),
#             InlineKeyboardButton(text="^", callback_data=f"up_month"),
#             InlineKeyboardButton(text="^", callback_data=f"up_year"),
#         ],
#         [
#             InlineKeyboardButton(text="v", callback_data=f"down_day"),
#             InlineKeyboardButton(text="v", callback_data=f"down_month"),
#             InlineKeyboardButton(text="v", callback_data=f"down_year"),
#         ]
#     ])
#
#
# @router.message(HabitStateFilter(HabitStates.enter_habit_description))
# async def habit_description(message: Message, user_cache: UserCache):
#     l = localizator.localizator.lang(user_cache.language)
#
#     if message.content_type != ContentType.TEXT:
#         await message.answer(l.wrong_type_habit_description)
#         return
#
#     if not is_valid_habit_name(message.text, max_words=50, max_length=300):
#         await message.answer(l.habit_name_too_long)
#         return
#
#     user_cache.habit.description = message.text
#     user_cache.state = HabitStates.enter_habit_start_date
#     await message.answer(l.enter_habit_start_date)
#
#     # next state is entering start date
#     # datetime.strptime(date_str, "%d-%m-%Y")
#     user_cache.habit.start_date = message.date.date()
#     send_message = await message.answer(message.date.strftime("%d-%m-%Y"), reply_markup=create_date_keyboard())
#     user_cache.temp_message_id = send_message.message_id
#
#
# @router.callback_query(HabitStateFilter(HabitStates.enter_habit_start_date))
# async def enter_habit_date(callback_query: CallbackQuery, user_cache: UserCache):
#     print(callback_query.data)
#     direction, period = callback_query.data.split('_')
#
#     current = user_cache.habit.start_date
#     day, month, year = current.day, current.month, current.year
#     change = 1 if direction == 'up' else -1
#
#     if period == 'day':
#         day += change
#     elif period == 'month':
#         month += change
#     elif period == 'year':
#         year += change
#     else:
#         assert False, f"Unexpected period: {period}"
#
#     _, days_in_month = calendar.monthrange(year, month)
#
#     if day == 0:
#         day = days_in_month
#     elif day > days_in_month:
#         day = 1
#
#     user_cache.habit.start_date = user_cache.habit.start_date.replace(year=year, month=month, day=day)
#     await callback_query.message.edit_text(user_cache.habit.start_date.strftime("%d-%m-%Y"), reply_markup=create_date_keyboard())
#     await callback_query.answer()
#
#
# @router.message(HabitStateFilter(HabitStates.enter_habit_start_date))
# async def enter_habit_date(message: Message, user_cache: UserCache):
#     l = localizator.localizator.lang(user_cache.language)
#
#     if message.content_type != ContentType.TEXT:
#         await message.answer(l.wrong_type_habit_name)
#         return
#
#     await message.delete()
#
#     try:
#         new_date = dateparser.parse(message.text).date()
#     except Exception as e:
#         print(f"enter_habit_date: {e.__class__.__name__}: {e}")
#         return
#
#     if user_cache.temp_message_id is None:
#         print(f"enter_habit_date: message with date not found: {user_cache.temp_message_id}")
#         return
#
#     try:
#         from bot import bot_instance
#         await bot_instance.edit_message_text(
#             new_date.strftime("%d-%m-%Y"),
#             message_id=user_cache.temp_message_id,
#             chat_id=message.chat.id,
#             reply_markup=create_date_keyboard(),
#         )
#         user_cache.habit.start_date = new_date
#     except Exception as e:
#         print(f"enter_habit_date: {e.__class__.__name__}: {e}")
#         return
