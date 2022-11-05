import datetime

from models.base_model import OrjsonBase


class TokenPair(OrjsonBase):
    """Token pair model for api response"""
    access_token: str
    refresh_token: str


class RefreshToken(OrjsonBase):
    refresh_token: str


class AccessToken(OrjsonBase):
    access_token: str


class TokenData(OrjsonBase):
    user_id: str
    role: str = 'default'
    exp: datetime.datetime


class JwtToken(TokenData):
    """Verified token"""
    value: str
