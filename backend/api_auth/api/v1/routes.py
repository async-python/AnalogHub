from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.config import AppSettings
from models.auth_models.bad_responses import Model400, Model401
from models.auth_models.token_models import JwtToken, TokenPair
from models.auth_models.users_models import (UserCreate, UserCreated,
                                             UserLogout, UserResponse)
from services.token_service import get_access_token, get_refresh_token
from services.user_service import UserService, get_user_service

router = APIRouter()
settings = AppSettings()


@router.post('/token', response_model=TokenPair,
             responses={400: {'model': Model400}})
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_view: UserService = Depends(get_user_service)):
    return await user_view.login(form_data.username, form_data.password)


@router.post('/refresh', response_model=TokenPair,
             responses={401: {'model': Model401}})
async def refresh_access_token(
        refresh_token: JwtToken = Depends(get_refresh_token),
        user_view: UserService = Depends(get_user_service)):
    return await user_view.refresh(refresh_token)


@router.post('/logout', response_model=UserLogout,
             responses={401: {'model': Model401}})
async def logout(
        access_token: JwtToken = Depends(get_access_token),
        user_service: UserService = Depends(get_user_service)):
    await user_service.logout(access_token)
    return UserLogout()


@router.get('/me', response_model=UserResponse,
            responses={401: {'model': Model401}})
async def get_user_info(
        access_token: JwtToken = Depends(get_access_token),
        user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user_detail(access_token)
    return UserResponse(**user.dict())


@router.post('/signup', response_model=UserCreated)
async def create_user(
        user: UserCreate,
        user_service: UserService = Depends(get_user_service)):
    await user_service.create(user)
    return UserCreated()
