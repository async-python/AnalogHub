from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import AppSettings
from models.auth_models.auth_models import (AccessToken, RefreshToken,
                                            TokenPair, User, UserLogout,
                                            UserCreate)
from services.auth_service import AuthService, get_auth_service

router = APIRouter()
settings = AppSettings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/token'
)


@router.post('/token', response_model=TokenPair)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth: AuthService = Depends(get_auth_service)):
    return await auth.create_token_pair(form_data.username, form_data.password)


@router.post('/token/refresh', response_model=TokenPair)
async def refresh_access_token(body: RefreshToken,
                               auth: AuthService = Depends(get_auth_service)):
    return await auth.refresh_token_pair(body.refresh_token)


@router.post('/token/logout', response_model=UserLogout)
async def delete_tokens(body: AccessToken,
                        auth: AuthService = Depends(get_auth_service)):
    await auth.delete_tokens(body.access_token)
    return UserLogout()


@router.get('/user/me', response_model=User)
async def read_user_me(token: str = Depends(oauth2_scheme),
                       auth: AuthService = Depends(get_auth_service)):
    return await auth.get_current_user(token)


@router.post('/user/register', response_model=User)
async def user_create(user: UserCreate,
                      auth: AuthService = Depends(get_auth_service)):
    return await auth.create_user(user)
