from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[Role] = Role.USER


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: Role


class VideoResponse(BaseModel):
    url: str
