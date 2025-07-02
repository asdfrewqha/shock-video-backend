from uuid import UUID

from fastapi import APIRouter, status
from uuid_v7.base import uuid7

from app.core.dependencies import badresponse
from app.models.auth_schemas import UserCreate, UserRegResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.passlib_hasher import Hasher
from app.models.token_manager import TokenManager


router = APIRouter()


@router.post("/register", response_model=UserRegResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    email_check = await adapter.get_by_value(User, "email", user.email)
    if email_check:
        return badresponse("Email lready exists", 409)
    username_check = await adapter.get_by_value(User, "username", user.username)
    if username_check:
        return badresponse("Username already exists", 409)

    new_id = UUID(uuid7())
    new_user = {
        "id": new_id,
        "email": user.email,
        "name": user.name,
        "username": f"@{user.username}",
        "hashed_password": Hasher.get_password_hash(user.password),
        "role": user.role,
        "description": user.description,
    }

    await adapter.insert(User, new_user)

    new_user_db = await adapter.get_by_id(User, new_id)

    access_token = TokenManager.create_token(
        {"sub": str(new_user_db.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = TokenManager.create_token(
        {"sub": str(new_user_db.id), "type": "refresh"},
        TokenManager.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return UserRegResponse(
        id=new_user_db.id,
        email=new_user_db.email,
        name=new_user_db.name,
        username=new_user_db.username,
        role=new_user_db.role,
        description=new_user_db.description,
        access_token=access_token,
        refresh_token=refresh_token,
    )
