from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    telegram_account = relationship("TelegramAccount", back_populates="user", uselist=False)

print("User model loaded")
print("Alembic sees these tables:", Base.metadata.tables.keys())
