from email.policy import default

from pydantic import BaseModel, Field, ConfigDict, constr
from datetime import date, datetime
from typing import Optional, List

from config import MAX_HABIT_NAME, MAX_HABIT_DESCRIPTION


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


class HabitBuffer(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=MAX_HABIT_NAME)] = None
    description: Optional[constr(strip_whitespace=True, min_length=1, max_length=MAX_HABIT_DESCRIPTION)] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    times_per_day: Optional[int] = Field(default=None, ge=1)

    model_config = ConfigDict(validate_assignment=True)
