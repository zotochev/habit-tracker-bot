from __future__ import annotations

import logging
from functools import partial
from itertools import chain
from collections import deque

from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

import bot

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


logger = logging.getLogger(__name__)


class Messenger:
    def __init__(self, telegram_id: int) -> None:
        self.__telegram_id = telegram_id
        self.__main_message_id: int | None = None
        self.__recv_messages_ids = []
        self.__sent_messages_ids = []

        self.__queue = deque()

    async def update_main_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
        self.__queue.append(
            partial(self.__update_main_message, text, reply_markup)
        )

    async def process_message(self) -> None:
        if self.__queue:
            task = self.__queue.popleft()
            await task()

    def register_recv_message(self, message_id: int) -> None:
        self.__recv_messages_ids.append(message_id)

    async def remove_temp_messages(self):
        for message_id in chain(self.__recv_messages_ids, self.__sent_messages_ids):
            if message_id == self.__main_message_id:
                continue

            logger.warning(f"{self.__class__.__name__}.remove_temp_messages(mm={self.__main_message_id}): {message_id}")
            try:
                await bot.bot_instance.delete_message(
                    self.__telegram_id,
                    message_id=message_id,
                )
            except Exception as e:
                logger.warning(f"{self.__class__.__name__}.remove_temp_messages: {e.__class__.__name__}: {e}")

        self.__recv_messages_ids.clear()
        self.__sent_messages_ids.clear()

    async def __update_main_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
        try:
            await self.__edit_message(text, reply_markup)
        except TelegramAPIError as e:
            logger.warning(f"{self.__class__.__name__}: update_main_message(mm={self.__main_message_id}): {e.__class__.__name__}: {e}")

            match e.message:
                case 'Bad Request: message to edit not found':
                    if self.__main_message_id is not None and self.__main_message_id not in self.__sent_messages_ids:
                        self.__sent_messages_ids.append(self.__main_message_id)
                    self.__main_message_id = None

                    await self.send_message(text, reply_markup)
                case 'Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
                    pass

        except Exception as e:
            logger.error(f"{self.__class__.__name__}: update_main_message(mm={self.__main_message_id}): {e.__class__.__name__}: {e}")

    async def __edit_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> Message:
        return await bot.bot_instance.edit_message_text(
            text=text,
            chat_id=self.__telegram_id,
            message_id=self.__main_message_id,
            reply_markup=reply_markup,
        )

    async def send_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> Message:
        message = await bot.bot_instance.send_message(
            chat_id=self.__telegram_id,
            text=text,
            reply_markup=reply_markup,
        )
        if self.__main_message_id is None:
            self.__main_message_id = message.message_id
        else:
            self.__sent_messages_ids.append(message.message_id)
        return message
