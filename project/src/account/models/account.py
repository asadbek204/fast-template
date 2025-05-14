from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import BaseModel
from sqlalchemy import String
from src.database.types import str_64, str_256
from src.account.manager import UserManager
from datetime import date


class AccountModel(BaseModel, UserManager):
    __tablename__ = 'accounts'

    username: Mapped[str_64] = mapped_column(unique=True)
    password: Mapped[str_256]
    phone: Mapped[str] = mapped_column(String(length=13), unique=True, nullable=True)
    sessions: Mapped[list["SessionModel"]] = relationship(back_populates='user')
    birth_date: Mapped[date]
    gender: Mapped[bool]

    def __str__(self):
        return f"<AccountModel: (username={self.username}, phone={self.phone})>"

from .session import SessionModel