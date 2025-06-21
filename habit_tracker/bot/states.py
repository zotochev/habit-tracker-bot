from enum import Enum, auto


class HabitStates(Enum):
    init = auto()
    end = auto()
    command_choose_language = auto()
    choose_language = auto()
    wait_command = auto()

    command_add_habit = auto()

    # wait_start_enter_habit = auto()
    # enter_habit_name = auto()
    # enter_habit_description = auto()
    # enter_habit_start_date = auto()
