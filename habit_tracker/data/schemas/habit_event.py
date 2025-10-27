from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class HabitEventBase(BaseModel):
    timestamp: Optional[datetime] = None  # Defaults to now on DB side


class HabitEventCreate(HabitEventBase):
    habit_id: int


class HabitEvent(HabitEventBase):
    id: int
    notification_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitStatistics(BaseModel):
    habit_id: int
    name: str

    percent_complete: int                 # overall completion %
    today_done: int                       # how many times done today
    times_per_day: int                    # how many needed per day
    current_streak: int                   # consecutive full days done

    week_done: int                        # total completions this week
    week_expected: int                    # expected completions this week

    month_done: int                       # total completions this month
    month_expected: int                   # expected completions this month


class CommonProgress(BaseModel):
    habit_count: int
    percent_complete: int
    total_completed: int
    total_expected: int

    today_done: int
    today_expected: int
    week_done: int
    week_expected: int
    month_done: int
    month_expected: int
