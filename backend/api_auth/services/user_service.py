import secrets
from functools import lru_cache

from fastapi import Depends, HTTPException
from starlette import status

from models.auth_models.token_models import JwtToken, TokenData, TokenPair
from models.auth_models.users_models import UserCreate, UserDB, UserLoad
from services.redis_service import RedisService, get_redis_service
from services.sql_service import SqlService, get_sql_service
from utils.exceptions import credentials_exception
from utils.password import get_password_hash, verify_password
from utils.token import TokenUtil


class UserService:

    def __init__(
            self, redis_service: RedisService,
            sql_service: SqlService) -> None:
        self.redis_sv = redis_service
        self.sql_sv = sql_service

    async def _authenticate_user(
            self, email: str, password: str) -> UserDB:
        user: UserDB = await self.sql_sv.get_user_by_email(email)
        if not user or not verify_password(password, user.password, user.salt):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Incorrect username or password')
        if user.disabled or not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='User not active or disabled')
        return user

    async def create(self, user: UserCreate):
        exist = await self.sql_sv.check_user_exists(user.email)
        if exist:
            raise HTTPException(422, detail='User exists')
        salt = secrets.token_urlsafe(50)
        password_hash = get_password_hash(salt + user.password)
        user_data = user.dict()
        payload = {'salt': salt, 'password': password_hash}
        user_data.update(payload)
        new_user = UserLoad(**user_data)
        # TODO: add email verify
        # await send_mail(subject='hi', email=EmailSchema(
        # email='vardeath@yandex.ru', body={'hi': 'hello'}), template_name='hello')
        await self.sql_sv.create_user(new_user)

    async def refresh(self, refresh_token: JwtToken):
        token_data = TokenData(**refresh_token.dict())
        access_token = TokenUtil.create_access_token(token_data.dict())
        new_refresh_token = TokenUtil.create_refresh_token(
            token_data.dict())
        await self.redis_sv.save_refresh_token(
            token_data.user_id, new_refresh_token)
        return TokenPair(
            access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, token: JwtToken):
        await self.redis_sv.save_invalid_access_token(
            token.value, token.exp)
        await self.redis_sv.delete_refresh_token(token.user_id)

    async def login(
            self, email: str, password: str) -> TokenPair:
        user: UserDB = await self._authenticate_user(email, password)
        user_id = str(user.id)
        payload = {'sub': user_id, 'role': user.role}
        access_token = TokenUtil.create_access_token(payload)
        refresh_token = TokenUtil.create_refresh_token(payload)
        await self.redis_sv.save_refresh_token(user_id, refresh_token)
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token)

    async def get_user_detail(self, token: JwtToken):
        user: UserDB = await self.sql_sv.get_user_by_id(
            token.user_id)
        if user is None:
            raise credentials_exception
        if user.disabled or not user.is_active:
            raise HTTPException(status_code=400, detail='Inactive user')
        return user


@lru_cache()
def get_user_service(redis_sv=Depends(get_redis_service),
                     postgres_sv=Depends(get_sql_service)) -> UserService:
    return UserService(redis_sv, postgres_sv)
