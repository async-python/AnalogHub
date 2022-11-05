from typing import List, Union

from models.base_model import OrjsonBase


class TokenPair(OrjsonBase):
    access_token: str
    refresh_token: str


class RefreshToken(OrjsonBase):
    refresh_token: str


class AccessToken(OrjsonBase):
    access_token: str


class TokenData(OrjsonBase):
    username: Union[str, None] = None
    scopes: List[str] = []


class UserCreate(OrjsonBase):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None


class User(OrjsonBase):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    scopes: Union[list[str], None] = None


class UserInDB(User):
    hashed_password: str


class UserRegister(OrjsonBase):
    logout: str = 'Ok'


class UserLogout(OrjsonBase):
    logout: str = 'Ok'
