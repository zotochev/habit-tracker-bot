from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class HabitUpdate(HabitBase):
    id: int
    user_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    times_per_day: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Habit(HabitBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
