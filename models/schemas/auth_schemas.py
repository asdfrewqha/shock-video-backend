from pydantic import BaseModel, UUID4
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
    avatar_url: str


class VideoResponse(BaseModel):
    id: UUID4
    url: str
    author_id: int
    views: int
    likes: int
    dislikes: int
    description: str


class VideoRequest(BaseModel):
    url: Optional[str] = ""
    uuid: Optional[str] = ""
