from functools import lru_cache

from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer

from core.config import AppSettings
from models.auth_models.token_models import JwtToken, TokenData
from models.auth_models.users_models import UserDB
from services.redis_service import RedisService, get_redis_service
from services.sql_service import SqlService, get_sql_service
from utils.exceptions import credentials_exception
from utils.token import TokenUtil

settings = AppSettings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/token', scheme_name="JWT")


class TokenService:
    def __init__(
            self, redis_service: RedisService,
            sql_service: SqlService) -> None:
        self.redis_sv = redis_service
        self.sql_sv = sql_service

    async def decode_access_token(self, token: str) -> JwtToken:
        await self.check_valid_access_token(token)
        token_data: TokenData = TokenUtil.decode_access_token(token)
        return JwtToken(**token_data.dict(), value=token)

    async def decode_refresh_token(self, token: str) -> JwtToken:
        token_data: TokenData = TokenUtil.decode_access_token(token)
        await self.check_valid_refresh_token(token_data.user_id, token)
        return JwtToken(**token_data.dict(), value=token)

    async def check_valid_access_token(self, token: str):
        invalid = await self.redis_sv.check_access_token_invalid(token)
        if invalid:
            raise credentials_exception

    async def check_valid_refresh_token(self, user_id: str, token: str):
        token_db = await self.redis_sv.get_refresh_token(user_id)
        if not token_db or token != token_db:
            raise credentials_exception


# Depend
@lru_cache()
def get_token_service(redis_sv=Depends(get_redis_service),
                      postgres_sv=Depends(get_sql_service)):
    return TokenService(redis_sv, postgres_sv)


async def get_access_token(
        token: str = Depends(oauth2_scheme),
        check_service: TokenService = Depends(get_token_service)) -> JwtToken:
    return await check_service.decode_access_token(token)


async def get_refresh_token(
        refresh_token: str = Form(),
        check_service: TokenService = Depends(get_token_service)) -> JwtToken:
    return await check_service.decode_refresh_token(refresh_token)
