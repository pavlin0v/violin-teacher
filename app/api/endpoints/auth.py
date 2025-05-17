import secrets
import time
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages, deps
from app.api.api_messages import ACCESS_TOKEN_RESPONSES, REFRESH_TOKEN_RESPONSES
from app.core.config import get_settings
from app.core.security.jwt import create_jwt_token
from app.core.security.password import (
    DUMMY_PASSWORD,
    get_password_hash,
    verify_password,
)
from app.models.models import RefreshToken, User
from app.schemas.requests import RefreshTokenRequest, UserCreateRequest
from app.schemas.responses import AccessTokenResponse, UserResponse



router = APIRouter()



@router.post(
    "/access-token",
    response_model=AccessTokenResponse,
    responses=ACCESS_TOKEN_RESPONSES,
    description="OAuth2 compatible token, get an access token for future requests using username and password",
)
async def login_access_token(
        session: AsyncSession = Depends(deps.get_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> AccessTokenResponse:
    user = await session.scalar(select(User).where(User.login == form_data.username))

    if user is None:
        # this is naive method to not return early
        verify_password(form_data.password, DUMMY_PASSWORD)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.PASSWORD_INVALID,
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.PASSWORD_INVALID,
        )

    jwt_token = create_jwt_token(user_id=user.user_id)


    refresh_token = RefreshToken(
        user_id=user.user_id,
        refresh_token=secrets.token_urlsafe(32),
        exp=int(time.time() + get_settings().security.refresh_token_expire_secs),
    )
    session.add(refresh_token)
    await session.commit()

    return AccessTokenResponse(
        access_token=jwt_token.access_token,
        expires_at=jwt_token.payload.exp,
        refresh_token=refresh_token.refresh_token,
        refresh_token_expires_at=refresh_token.exp,
    )

@router.post(
    "/refresh-token",
    response_model=AccessTokenResponse,
    responses=REFRESH_TOKEN_RESPONSES,
    description="OAuth2 compatible token, get an access token for future requests using refresh token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> AccessTokenResponse:
    token = await session.scalar(
        select(RefreshToken)
        .where(RefreshToken.refresh_token == data.refresh_token)
        .with_for_update(skip_locked=True)
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.REFRESH_TOKEN_NOT_FOUND,
        )
    elif time.time() > token.exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.REFRESH_TOKEN_EXPIRED,
        )
    elif token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.REFRESH_TOKEN_ALREADY_USED,
        )

    token.used = True
    session.add(token)

    jwt_token = create_jwt_token(user_id=token.user_id)

    refresh_token = RefreshToken(
        user_id=token.user_id,
        refresh_token=secrets.token_urlsafe(32),
        exp=int(time.time() + get_settings().security.refresh_token_expire_secs),
    )
    session.add(refresh_token)
    await session.commit()

    return AccessTokenResponse(
        access_token=jwt_token.access_token,
        expires_at=jwt_token.payload.exp,
        refresh_token=refresh_token.refresh_token,
        refresh_token_expires_at=refresh_token.exp,
    )

@router.post(
    "/register",
    response_model=UserResponse,
    description="Create new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_user(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.login == new_user.login))
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.USER_ALREADY_EXISTS,
        )

    user = User(
        login=new_user.login,
        hashed_password=get_password_hash(new_user.password),
        name="Смешарик"
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        # Извлекаем сырой текст ошибки
        raw_msg = str(e.orig)
        # Генерируем понятный ответ
        if 'ix_users_login' in raw_msg:
            detail = "Пользователь с таким логином уже зарегистрирован"
        elif re.search(r'foreign key constraint', raw_msg, re.IGNORECASE):
            detail = "Нарушено ограничение связи в данных"
        else:
            detail = raw_msg  # fallback на оригинал
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    return user


