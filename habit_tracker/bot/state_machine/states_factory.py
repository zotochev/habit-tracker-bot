from bot.states import HabitStates


STATES_FACTORY = {}


def register_state(state: HabitStates):
    def _wrapper(cls):
        global STATES_FACTORY

        cls.state = state
        STATES_FACTORY[state] = cls

        return cls
    return _wrapper
