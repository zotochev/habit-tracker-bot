from __future__ import annotations

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones, ZoneInfoNotFoundError

from timezonefinder import TimezoneFinder
from aiogram.types import Message, CallbackQuery, Location, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from bot.state_machine.states_factory import register_state
from bot.states import HabitStates
from bot.state_machine.states_interfaces import IState, IImmediateHandle

from core import localizator

from typing import TYPE_CHECKING

from data.schemas import UserUpdate

if TYPE_CHECKING:
    from bot.cache import UserCache
    from data.repositories.backend_repository.backend_repository import BackendRepository


tf = TimezoneFinder()
logger = logging.getLogger(__name__)


@register_state(HabitStates.choose_timezone)
class ChoseTimezoneState(IState):
    MAX_ZONES_BUTTONS = 10
    CONFIRM_CALLBACK_DATA = 'confirm_timezone'

    def __init__(self,
                 backend_repository: BackendRepository,
                 user_cache: UserCache,
                 state_factory: dict[HabitStates, IState.__class__],
                 **kwargs,
                 ) -> None:
        super().__init__(backend_repository, user_cache, state_factory, **kwargs)
        self._current_timezone = ZoneInfo("UTC")
        self._found_zones = None
        self._message = None

    async def handle(self, message: Message | CallbackQuery) -> IState:
        if isinstance(message, Message) and message.content_type == ContentType.LOCATION:
            return await self.__handle_location(message)
        else:
            return await super().handle(message)

    async def _handle_message(self, message: Message) -> IState:
        zones = [zone for zone in available_timezones() if message.text.lower().strip() in zone.lower()]
        l = localizator.localizator.lang(self._user_cache.language)

        match len(zones):
            case 0:
                self._message = l.timezone_no_timezones
            case 1:
                self._current_timezone = ZoneInfo(zones[0])
            case number_of_zones if number_of_zones <= self.MAX_ZONES_BUTTONS:
                self._found_zones = zones
            case _:
                self._message = l.timezone_too_many_timezones.format(num_zones=len(zones), text=message.text)

        return await self._handle(message.text)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> IState:
        message_text = callback_query.data
        l = localizator.localizator.lang(self._user_cache.language)

        try:
            if message_text == self.CONFIRM_CALLBACK_DATA:
                await self._backend_repository.update_user(
                    UserUpdate(id=self._user_cache.backend_id, timezone=self._current_timezone.key),
                )
                await callback_query.answer(l.timezone_updated_to.format(timezone=self._current_timezone.key))
                return self._create(HabitStates.end)
            else:
                self._current_timezone = ZoneInfo(message_text)
                await callback_query.answer()
        except ZoneInfoNotFoundError as e:
            logger.error(f"{self.__class__.__name__}: {e.__class__.__name__}: {e}")
            await callback_query.answer(l.timezone_not_found.format(text=message_text))

        return await self._handle(message_text)

    async def _handle(self, message_text: str) -> IState:
        await self.__update_message()

        self._found_zones = None
        self._message = None
        return self

    async def on_enter(self) -> None:
        await super().on_enter()
        await self.__update_message()

    def is_handable(self, context_type) -> bool:
        result = super().is_handable(context_type)
        return result or context_type == ContentType.LOCATION

    async def __handle_location(self, message: Message) -> IState:
        timezone = await self.__get_timezone_from_location(message.location)
        if timezone is not None and timezone != self._current_timezone:
            self._current_timezone = timezone

        return await self._handle('')

    @staticmethod
    async def __get_timezone_from_location(location: Location) -> ZoneInfo | None:
        lat = location.latitude
        lon = location.longitude

        timezone_str = tf.timezone_at(lat=lat, lng=lon)

        if timezone_str:
            return ZoneInfo(timezone_str)

    def __generate_text(self):
        """
        🕒 Your current timezone: Europe/Belgrade
        🗓️ Local time: 2025-07-07 14:23
        🌐 UTC offset: +02:00
        """
        l = localizator.localizator.lang(self._user_cache.language)
        now = datetime.now(self._current_timezone)
        offset_str = self.__get_offset_from_zone_name(self._current_timezone.key)

        text = (
            f"{l.timezone_current}: {self._current_timezone.key}\n"
            f"{l.timezone_local_time}: {now.strftime('%Y-%m-%d %H:%M')}\n"
            f"{l.timezone_offset}: {offset_str}"
        )

        if self._message:
            text += '\n\n{}'.format(self._message)
        return text

    @staticmethod
    def __get_offset_from_zone_name(zone_name: str) -> str:
        tz = ZoneInfo(zone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()  # returns a timedelta

        sign = "+" if offset.total_seconds() >= 0 else "-"
        total_minutes = abs(int(offset.total_seconds()) // 60)
        hh = total_minutes // 60
        mm = total_minutes % 60

        return f"UTC{sign}{hh:02}:{mm:02}"

    def __generate_keyboard(self):
        l = localizator.localizator.lang(self._user_cache.language)

        if self._found_zones:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            for zone_name in self._found_zones:
                keyboard.inline_keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f'{zone_name}:{self.__get_offset_from_zone_name(zone_name)}',
                            callback_data=f'{zone_name}',
                        ),
                    ]
                )
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=l.button_confirm,
                    callback_data=self.CONFIRM_CALLBACK_DATA,
                ),
            ]])

        return keyboard

    async def __update_message(self):
        text = self.__generate_text()
        keyboard = self.__generate_keyboard()
        await self._user_cache.messenger.update_main_message(text, keyboard)
