from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
    id: UUID
    username: str
    role: Role
    avatar_url: Optional[str] = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class VideoResponse(BaseModel):
    id: UUID
    sup_url: str
    serv_url: str
    author_id: UUID
    views: int
    likes: int
    dislikes: int
    description: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class VideoModel(BaseModel):
    url: Optional[str] = ""
    uuid: Optional[str] = ""


class UpdateVideoContent(BaseModel):
    description: str
