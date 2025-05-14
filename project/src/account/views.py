from typing import Annotated
from fastapi import APIRouter, Depends, Body, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database.database import get_session
from .schemas import Token, User, UserInDB
from .models import AccountModel, SessionModel
from .manager import credentials_exception, oauth2_scheme, UserManager
from sqlalchemy import select
from fastapi import HTTPException, status

router = APIRouter(prefix='/account', tags=['account'])


@router.post("/token", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session)
) -> Token:
    user: AccountModel | None = (await session.execute(
        select(AccountModel).filter(AccountModel.username == form_data.username)
    )).scalars().one_or_none()
    if not user:
        raise credentials_exception
    if user.verify_password(form_data.password, user.password):
        access_token, user_session_id = await user.create_access_token(
            session,
            data={"username": user.username},
        )
        refresh_token = user.create_refresh_token(data={"username": user.username}, user_session_id=user_session_id)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    raise credentials_exception


@router.post("/refresh", response_model=Token)
async def refresh(
        token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]
):
    access_token, = await UserManager.refresh_access_token(token, session)
    return Token(access_token=access_token, token_type="bearer", refresh_token=token)


@router.post('/')
async def create_account(response: Response, data: UserInDB = Body(), session: AsyncSession = Depends(get_session)):
    user = AccountModel(username=data.username, password=AccountModel.get_password_hash(data.password),
                        phone=data.phone, birth_date=data.birth_date, gender=data.gender)
    try:
        session.add(user)
        await session.commit()
    except IntegrityError as err:
        field = str(err.orig).split('.')[-1]
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "detail": [
                {
                    "type": "conflict",
                    "loc": [
                        "body",
                        field
                    ],
                    "msg": f"{field} already exists",
                    "input": data
                }
            ]
        }
    return User(username=user.username, phone=user.phone, birth_date=user.birth_date, gender=user.gender)


@router.get("/", response_model=User)
async def get_me(
        user_session: SessionModel = Depends(AccountModel.get_current_user),
):
    if user_session.active:
        return User(username=user_session.user.username, phone=user_session.user.phone, birth_date=user_session.user.birth_date, gender=user_session.user.gender)
    raise HTTPException(status_code=400, detail="Inactive user")
