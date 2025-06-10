from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from core.database.db import Base
from core.database.mixins import TimestampMixin


class HabitEvent(Base, TimestampMixin):
    __tablename__ = 'habit_events'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)

    habit = relationship("Habit", back_populates="events")

    def __repr__(self):
        return f"<HabitEvent(id={self.id}, habit_id={self.habit_id}, created_at={self.created_at})>"
