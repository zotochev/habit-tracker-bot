from __future__ import annotations

import logging
from itertools import chain

from aiogram.types import Message

import bot

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


logger = logging.getLogger(__file__)


class Messenger:
    def __init__(self, telegram_id: int) -> None:
        self.__telegram_id = telegram_id
        self.__main_message_id: int | None = None
        self.__recv_messages_ids = []
        self.__sent_messages_ids = []

    async def update_main_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
        try:
            await self.edit_message(text, reply_markup)
        except Exception as e:
            if self.__main_message_id is not None and self.__main_message_id not in self.__sent_messages_ids:
                self.__sent_messages_ids.append(self.__main_message_id)

            self.__main_message_id = None
            logger.warning(f"{self.__class__.__name__}: update_main_message(mm={self.__main_message_id}): {e.__class__.__name__}: {e}")
            await self.send_message(text, reply_markup)

    async def edit_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> Message:
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
