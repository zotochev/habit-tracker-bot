from enum import Enum, auto


class HabitStates(Enum):
    init = auto()
    end = auto()
    command_choose_language = auto()
    choose_language = auto()
    wait_command = auto()

    command_add_habit = auto()
    add_habit = auto()
    command_list_habits = auto()
    list_habits = auto()
