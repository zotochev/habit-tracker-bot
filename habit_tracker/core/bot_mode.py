from enum import StrEnum, auto


class BotMode(StrEnum):
    polling = auto()
    webhook = auto()
