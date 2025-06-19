import enum
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict

from .telegram_account import TelegramAccount


class LanguageEnum(str, enum.Enum):
    RU = 'ru'
    EN = 'en'

    @classmethod
    def ALL(cls):
        return (
            cls.RU,
            cls.EN,
        )


class UserBase(BaseModel):
    name: str
    language: LanguageEnum = LanguageEnum.RU


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: int
    name: Optional[str] = None
    language: Optional[LanguageEnum] = None


class User(UserBase):
    id: int
    telegram_account: Optional[TelegramAccount] = None

    model_config = ConfigDict(from_attributes=True)
