from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from pydantic import ValidationError

from core.config import AppSettings
from models.auth_models.token_models import TokenData

settings = AppSettings()


class TokenUtil:
    @classmethod
    def _decode_token(cls, token: str, key: str) -> TokenData:
        try:
            payload = jwt.decode(
                token, key, algorithms=[settings.algorithm])
            user_id: str = payload.get('sub')
            token_role = payload.get('role')
            token_ex = payload.get('exp')
            token_data = TokenData(
                role=token_role, user_id=user_id, exp=token_ex)
            return token_data
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except (JWTError, ValidationError, JWTClaimsError):
            raise HTTPException(status_code=401, detail='Invalid token')

    @classmethod
    def _create_token(cls, data: dict, key: str) -> str:
        return jwt.encode(
            data, key, algorithm=settings.algorithm)

    @classmethod
    def decode_access_token(cls, token: str) -> TokenData:
        return cls._decode_token(token, settings.secret_key)

    @classmethod
    def decode_refresh_token(cls, token: str) -> TokenData:
        return cls._decode_token(token, settings.secret_key_refresh)

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes),
            'iat': datetime.utcnow(),
        }
        return cls._create_token(data | payload, settings.secret_key)

    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=settings.refresh_token_expire_days),
            'iat': datetime.utcnow(),
        }
        return cls._create_token(data | payload, settings.secret_key_refresh)
