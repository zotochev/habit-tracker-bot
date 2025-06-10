from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    times_per_day: int = Field(default=1, ge=1)


class HabitCreate(HabitBase):
    user_id: int


class Habit(HabitBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
