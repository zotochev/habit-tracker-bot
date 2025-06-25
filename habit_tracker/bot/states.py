from enum import Enum, auto


class HabitStates(Enum):
    init = auto()
    end = auto()
    command_choose_language = auto()
    choose_language = auto()
    wait_command = auto()

    command_add_habit = auto()
    add_habit = auto()
    command_todays_habits = auto()
    todays_habits = auto()
    my_habits = auto()
    edit_habit = auto()
