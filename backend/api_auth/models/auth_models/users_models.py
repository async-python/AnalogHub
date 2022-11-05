from typing import Optional, Union
from uuid import UUID

from pydantic import EmailStr, Field

from models.auth_models.token_models import TokenData
from models.base_model import OrjsonBase


class UserCreate(OrjsonBase):
    """Entry api User model"""
    username: str = Field(..., max_length=20)
    email: EmailStr = Field(...,)
    full_name: Union[str, None] = Field(None, max_length=100)
    password: str = Field(..., max_length=100)


class UserLoad(OrjsonBase):
    """User model for database loading"""
    username: str = Field(..., max_length=20)
    email: EmailStr = Field(...,)
    full_name: Union[str, None] = Field(None, max_length=100)
    disabled: bool = False
    is_active: bool = False
    role: str = 'default'
    password: str = Field(..., max_length=100)
    salt: str = Field(..., max_length=100)


class UserDB(UserLoad):
    """User model for extract from database"""
    id: UUID


class UserResponse(OrjsonBase):
    """User api response model"""
    id: UUID
    username: str
    email: str
    full_name: Union[str, None]
    role: str


class UserCreated(OrjsonBase):
    created: str = 'Ok'


class UserLogout(OrjsonBase):
    logout: str = 'Ok'
