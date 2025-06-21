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


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: int
    name: Optional[str] = None
    language: Optional[LanguageEnum] = None


class User(UserBase):
    id: int
    # telegram_id: Optional[TelegramAccount] = None
    telegram_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
