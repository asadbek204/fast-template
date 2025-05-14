from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import Mapped
from .database import Base
from .types import int_pk


class BaseModel(AbstractConcreteBase, Base):
    """
    - id : primary key for all nested models
    - __repr__ : base implementation for describing models
    """
    __abstract__ = True

    id: Mapped[int_pk]

    def __repr__(self) -> str:
        return f"<{self.__tablename__} (id={self.id})>"
