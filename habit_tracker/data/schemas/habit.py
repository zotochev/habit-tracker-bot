from enum import Enum, auto

from pydantic import BaseModel, Field, ConfigDict, constr
from datetime import date, datetime, time
from typing import Optional

from config import MAX_HABIT_NAME, MAX_HABIT_DESCRIPTION


class HabitRepeatType(Enum):
    daily = auto()
    weekly = auto()
    monthly = auto()


class HabitRepeatTypeMixin:
    def _get_index(self, day: date) -> int:
        match self.repeat_type:
            case HabitRepeatType.daily:
                return 0
            case HabitRepeatType.weekly:
                return day.weekday()
            case HabitRepeatType.monthly:
                return day.day - 1
            case _:
                raise AssertionError(f'Unexpected repeat_type: {self.repeat_type}')

    def is_day_set(self, day: date) -> bool:
        """
        Check if the bit at day_index is set.
        day_index starts from 0, where zero is Monday or 1 day of month
        """
        return bool((self.days_mask >> self._get_index(day)) & 1)

    def set_day(self, day: date) -> None:
        self.days_mask = self.days_mask | (1 << self._get_index(day))

    def unset_day(self, day: date) -> None:
        self.days_mask = self.days_mask & ~(1 << self._get_index(day))
        if self.days_mask == 0:
            self.days_mask = 1


class HabitBase(BaseModel, HabitRepeatTypeMixin):
    name: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    times_per_day: int = Field(default=1, ge=1)
    repeat_type: HabitRepeatType = HabitRepeatType.daily
    days_mask: int = 1
    notifications: list[time] | None = None


class HabitCreate(HabitBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class HabitUpdate(HabitBase):
    id: int
    user_id: int
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    times_per_day: int | None = None
    repeat_type: HabitRepeatType | None = None
    days_mask: int | None = None
    notifications: list[time] | None = None

    model_config = ConfigDict(from_attributes=True)


class Habit(HabitBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitProgress(HabitUpdate):
    user_id: Optional[int] = None
    times_did: Optional[int] = None


class HabitBuffer(BaseModel, HabitRepeatTypeMixin):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=MAX_HABIT_NAME)] = None
    description: Optional[constr(strip_whitespace=True, min_length=1, max_length=MAX_HABIT_DESCRIPTION)] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    times_per_day: Optional[int] = Field(default=1, ge=1)
    repeat_type: HabitRepeatType | None = None
    days_mask: int = 1
    notifications: list[time] | None = None

    model_config = ConfigDict(validate_assignment=True)


class HabitNotification(BaseModel):
    id: int
    user_id: int
    name: str
    notifications: list[time]

    model_config = ConfigDict(from_attributes=True)
