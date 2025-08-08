import enum
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict

from .telegram_account import TelegramAccount


class LanguageEnum(str, enum.Enum):
    ru = 'ru'
    en = 'en'

    @classmethod
    def all(cls):
        return (
            cls.ru,
            cls.en,
        )

    @classmethod
    def map(cls):
        return {
            cls.ru: "🇷🇺",
            cls.en: "🇬🇧",
        }


class UserBase(BaseModel):
    name: Optional[str] = None
    language: LanguageEnum = LanguageEnum.ru
    timezone: str = 'UTC'


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: int
    name: Optional[str] = None
    language: Optional[LanguageEnum] = None
    timezone: str | None = None


class User(UserBase):
    id: int
    telegram_account: TelegramAccount | None = None

    model_config = ConfigDict(from_attributes=True)
