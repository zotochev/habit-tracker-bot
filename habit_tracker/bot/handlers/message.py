from aiogram import Router
from aiogram.types import (
    Message,
)
from aiogram.enums import ChatType as ChatTypeEnum

import bot
from bot.cache import UserCache
from bot.state_machine.states.initial import logger


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
    return any(e.type == "bot_command" for e in entities)


@router.message(lambda message: not is_command_message(message))
async def habit_name(message: Message, user_cache: UserCache):
    if not user_cache.state_machine.is_handable(message.content_type):
        logger.warning(f"default message handler: wrong content_type: {message.content_type}")
        await message.delete()
        return

    if message.chat.type in [ChatTypeEnum.GROUP, ChatTypeEnum.SUPERGROUP]:
        await message.answer("I am not allowed in groups. Leaving...")
        await bot.bot_instance.leave_chat(message.chat.id)

    await user_cache.state_machine.handle(message)
    await user_cache.messenger.remove_temp_messages()
