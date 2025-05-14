from datetime import datetime
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
import typing

str_16 = typing.Annotated[str, String(16)]
str_32 = typing.Annotated[str, String(32)]
str_64 = typing.Annotated[str, String(64)]
str_128 = typing.Annotated[str, String(128)]
str_256 = typing.Annotated[str, String(256)]
str_512 = typing.Annotated[str, String(512)]
name = str_64 | None
username = typing.Annotated[str_32, mapped_column(unique=True)]
int_pk = typing.Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
auto_utcnow = typing.Annotated[datetime, mapped_column(default=datetime.utcnow, nullable=True)]
bool_default_false = typing.Annotated[bool, mapped_column(default=False, nullable=True)]
updated_at = typing.Annotated[datetime, mapped_column(nullable=True, default=None, onupdate=datetime.utcnow)]
