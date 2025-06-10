from pydantic import BaseModel
from typing import Optional

from .telegram_account import TelegramAccount


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    telegram_account: Optional[TelegramAccount] = None

    class Config:
        orm_mode = True
