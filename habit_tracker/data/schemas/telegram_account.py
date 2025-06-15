from pydantic import BaseModel, ConfigDict
from typing import Optional


class TelegramAccountBase(BaseModel):
    telegram_id: int


class TelegramAccountCreate(TelegramAccountBase):
    name: str


class TelegramAccount(TelegramAccountBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)
