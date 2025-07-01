from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    password: str
    role: Optional[Role] = Role.USER


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class UserRegResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    username: str
    role: Role
    access_token: str
    refresh_token: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    role: Role

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    name: str
    role: Role
    liked_videos: list
    disliked_videos: list

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
