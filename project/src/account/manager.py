from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from settings import settings
import jwt
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.database import AsyncSession, get_session
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.auth.secret_key
ALGORITHM = settings.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth.access_token_life_time
REFRESH_TOKEN_EXPIRE_MINUTES = settings.auth.refresh_token_life_time * 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="account/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class UserManager:

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    async def create_access_token(self, session: AsyncSession, data: dict):
        from .models.session import SessionModel
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        user_session = SessionModel(user_id=self.id)
        session.add(user_session)
        await session.commit()
        data.update({"exp": expire, 'type': 'access', "session_id": user_session.id})
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, user_session.id

    @staticmethod
    def create_refresh_token(data: dict, user_session_id: int):
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        data.update({"exp": expire, 'type': 'refresh', "session_id": user_session_id})
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def refresh_access_token(refresh_token: str, session: AsyncSession):
        from .models.session import SessionModel

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['type'] != 'refresh':
                raise credentials_exception
            if datetime.now() > payload['exp']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token is expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            session_id: int = int(payload.get("session_id"))
            if session_id is None:
                raise credentials_exception
            user_session: SessionModel = (await session.execute(
                select(SessionModel).filter(SessionModel.id == session_id).options(
                    joinedload(SessionModel.user)))).scalars().one_or_none()
            if user_session is None:
                raise credentials_exception
            access_token = await user_session.user.create_access_token(session, {'username': user_session.user.username})
            return access_token
        except (InvalidTokenError, ValueError):
            raise credentials_exception


    @staticmethod
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]):
        from .models.session import SessionModel

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['type'] != 'access':
                raise credentials_exception
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access token is expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            session_id: int = payload.get("session_id")
            user_session: SessionModel = (await session.execute(select(SessionModel).filter(SessionModel.id == session_id).options(joinedload(SessionModel.user)))).scalars().one_or_none()
            if not user_session:
                raise credentials_exception
            return user_session
        except (InvalidTokenError, ValueError):
            raise credentials_exception

    @staticmethod
    def verify_user(token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['type'] != 'access':
                raise credentials_exception
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access token is expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return True
        except (InvalidTokenError, ValueError):
            raise credentials_exception