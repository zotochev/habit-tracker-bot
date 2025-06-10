from pydantic import BaseModel
from typing import Optional


class TelegramAccountBase(BaseModel):
    telegram_id: int


class TelegramAccountCreate(TelegramAccountBase):
    user_id: int


class TelegramAccount(TelegramAccountBase):
    class Config:
        orm_mode = True
