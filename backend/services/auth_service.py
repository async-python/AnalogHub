from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import Depends, HTTPException
from jose import JWTError, jwt, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from passlib.context import CryptContext
from starlette import status

from core.config import AppSettings
from models.auth_models.auth_models import TokenData, TokenPair, UserInDB
from services.redis_service import RedisService, get_redis_service

settings = AppSettings()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'not enough permissions'},
)


class AuthService:
    def __init__(self, redis_sv: RedisService) -> None:
        self.redis_sv = redis_sv

    fake_users_db = {
        'johndoe': {
            'username': 'johndoe',
            'full_name': 'John Doe',
            "email": "johndoe@example.com",
            "scopes": ['me', 'items'],
            "hashed_password": '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            "disabled": False,
        },
        'alice': {
            "username": "alice",
            "full_name": "Alice Chains",
            "email": "alicechains@example.com",
            "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
            "disabled": True,
        },
    }

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def get_user(self, username: str):
        if username in self.fake_users_db:
            user_dict = self.fake_users_db[username]
            return UserInDB(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    async def create_access_token(self, data: dict) -> str:
        payload = {
            'type': 'access_token',
            'exp': datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes),
            'iat': datetime.utcnow(),
        }
        to_encode = data.copy()
        to_encode.update(payload)
        access_token = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm)
        await self.redis_sv.save_access_token(data.get('sub'), access_token)
        return access_token

    async def create_refresh_token(self, data: dict) -> str:
        payload = {
            'type': 'refresh_token',
            'exp': datetime.utcnow() + timedelta(
                days=settings.refresh_token_expire_days),
            'iat': datetime.utcnow(),
        }
        to_encode = data.copy()
        to_encode.update(payload)
        refresh_token = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm)
        await self.redis_sv.save_refresh_token(data.get('sub'), refresh_token)
        return refresh_token

    async def get_current_user(
            self, token: str, permissions: list[str] = None):
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get('sub')
            token_type: str = payload.get('type')
            if username is None or token_type != 'access_token':
                raise credentials_exception
            token_scopes = payload.get('scopes', [])
            token_data = TokenData(scopes=token_scopes, username=username)
        except (JWTError, ExpiredSignatureError, JWTClaimsError):
            raise credentials_exception
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        await self.verify_token_redis(user.username, token, token_type)
        if user.disabled:
            raise HTTPException(status_code=400, detail='Inactive user')
        if permissions:
            for scope in permissions:
                if scope not in token_data.scopes:
                    raise credentials_exception
        return user

    async def verify_token_redis(self,
                                 username: str, token: str, token_type: str):
        if token_type == 'access_token':
            token_db = await self.redis_sv.get_access_token(username)
        else:
            token_db = await self.redis_sv.get_refresh_token(username)
        if not token_db or token != token_db:
            raise HTTPException(status_code=400, detail='Token not valid')

    async def create_token_pair(
            self, username: str, password: str) -> TokenPair:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=400,
                                detail='Incorrect username or password')
        payload = {'sub': user.username, 'scopes': user.scopes}
        access_token = await self.create_access_token(data=payload)
        refresh_token = await self.create_refresh_token(data=payload)
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token)

    async def refresh_token_pair(self, refresh_token: str) -> TokenPair:
        try:
            token_data = jwt.decode(
                refresh_token, settings.secret_key,
                algorithms=[settings.algorithm])
            username = token_data.get('sub')
            token_type = token_data.get('type')
            await self.verify_token_redis(username, refresh_token, token_type)
            access_token = await self.create_access_token(data=token_data)
            return TokenPair(
                access_token=access_token, refresh_token=refresh_token)
        except (JWTError, ExpiredSignatureError, JWTClaimsError):
            raise credentials_exception

    async def delete_tokens(self, access_token: str):
        try:
            token_data = jwt.decode(
                access_token, settings.secret_key,
                algorithms=[settings.algorithm])
            username = token_data.get('sub')
            await self.redis_sv.delete_access_token(username)
            await self.redis_sv.delete_refresh_token(username)
        except (JWTError, ExpiredSignatureError, JWTClaimsError):
            raise credentials_exception


# Depend
@lru_cache()
def get_auth_service(redis_sv=Depends(get_redis_service)):
    return AuthService(redis_sv)
