from enum import StrEnum, auto


class HabitField(StrEnum):
    name = auto()
    description = auto()
    times_per_day = auto()
    start_date = auto()
    end_date = auto()
    repeat_type = auto()
    days_mask = auto()
    notifications = auto()
