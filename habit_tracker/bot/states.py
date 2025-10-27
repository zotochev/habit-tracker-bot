from enum import Enum, auto


class HabitStates(Enum):
    init = auto()
    end = auto()
    command_choose_language = auto()
    choose_language = auto()
    wait_command = auto()
    progress = auto()
    progress_habit = auto()

    command_add_habit = auto()
    add_habit = auto()
    todays_habits = auto()
    todays_notifications = auto()
    my_habits = auto()
    edit_habit = auto()
    delete_habit = auto()

    help_command = auto()
    registration = auto()
    choose_timezone = auto()

    settings = auto()
