from enum import Enum, auto


class HabitStates(Enum):
    init = auto()
    wait_start_enter_habit = auto()
    enter_habit_name = auto()
    enter_habit_description = auto()
    enter_habit_start_date = auto()
