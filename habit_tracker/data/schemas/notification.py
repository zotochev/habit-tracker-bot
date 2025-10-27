from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import time

from core.utils import seconds_to_time


class NotificationBase(BaseModel):
    time_in_seconds: Optional[int] = None  # 0..86399; None means unscheduled

    def time(self) -> time:
        return seconds_to_time(self.time_in_seconds)


class NotificationCreate(NotificationBase):
    habit_id: int


class Notification(NotificationBase):
    notification_id: int | None = None
    habit_id: int

    model_config = ConfigDict(from_attributes=True)
