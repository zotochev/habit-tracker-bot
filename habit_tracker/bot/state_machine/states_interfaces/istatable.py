from __future__ import annotations
from abc import ABC

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.states import HabitStates


class IStatable(ABC):
    state: HabitStates = None
