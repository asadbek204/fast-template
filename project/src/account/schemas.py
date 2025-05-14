import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class User(BaseModel):
    username: str
    phone: Optional[str] = Field(default=None, max_length=16, min_length=13)
    birth_date: datetime.date
    gender: bool


class UserInDB(User):
    password: str
