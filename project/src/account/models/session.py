from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import BaseModel
from sqlalchemy import ForeignKey


class SessionModel(BaseModel):
    __tablename__ = 'sessions'
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete='CASCADE'))
    user: Mapped['AccountModel'] = relationship(back_populates="sessions")
    active: Mapped[bool] = mapped_column(default=True)

    def __str__(self):
        return f"<SessionModel: (user={self.user}, active={self.active})>"

from src.account.models.account import AccountModel
