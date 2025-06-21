from bot.states import HabitStates

from bot.state_machine.states import (
    InitState,
    ChooseLanguage,
    ChooseLanguageCommand,
    WaitCommand,
    EndState,
    AddHabitCommandState,
    AddHabitState,
)


STATES_FACTORY = {
    state_class.state: state_class
    for state_class in (
        InitState,
        ChooseLanguage,
        ChooseLanguageCommand,
        WaitCommand,
        EndState,
        AddHabitCommandState,
        AddHabitState,
    )
}
