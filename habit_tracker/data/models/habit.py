from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from core.database.db import Base
from core.database.mixins import TimestampMixin


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    start_date = Column(DateTime, default=func.now(), nullable=False)
    end_date = Column(DateTime, nullable=True)

    times_per_day = Column(Integer, default=1)

    user_id = Column(Integer, ForeignKey("users.id"))

    events = relationship("HabitEvent", back_populates="habit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Habit(id={self.id}, name={self.name}, times_per_day={self.times_per_day})>"
