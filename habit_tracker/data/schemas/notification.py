from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import time

from core.utils import seconds_to_time, timezone_offset


class NotificationBase(BaseModel):
    time_in_seconds: Optional[int] = None  # 0..86399; None means unscheduled

    def time(self, time_zone: str) -> time:
        if self.time_in_seconds is None:
            # return midnight by default for formatting, caller should handle None separately
            return time(0, 0)
        return seconds_to_time(self.time_in_seconds + int(timezone_offset(time_zone).total_seconds()))


class NotificationCreate(NotificationBase):
    habit_id: int


class Notification(NotificationBase):
    notification_id: int | None = None
    habit_id: int
    user_id: Optional[int] = None  # filled by backend for cross-user notifications
    habit_name: Optional[str] = None  # optional convenience field

    model_config = ConfigDict(from_attributes=True)
