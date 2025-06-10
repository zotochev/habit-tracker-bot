from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List


class HabitEventBase(BaseModel):
    timestamp: Optional[datetime] = None  # Defaults to now on DB side


class HabitEventCreate(HabitEventBase):
    habit_id: int


class HabitEvent(HabitEventBase):
    id: int
    habit_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
