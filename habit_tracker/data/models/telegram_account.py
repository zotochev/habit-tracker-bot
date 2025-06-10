from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from core.database.db import Base


class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"
    telegram_id = Column(BigInteger, primary_key=True, unique=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="telegram_account")
