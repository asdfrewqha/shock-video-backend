from uuid import UUID, uuid5

from fastapi import APIRouter, status

from config import UUID_SHA
from dependencies import badresponse
from models.db_source.db_adapter import adapter
from models.hashing.passlib_hasher import Hasher
from models.schemas.auth_schemas import UserCreate, UserRegResponse
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager


router = APIRouter()


@router.post("/register", response_model=UserRegResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    email_check = await adapter.get_by_value(User, "email", user.email)
    if email_check:
        return badresponse("Email lready exists", 409)
    username_check = await adapter.get_by_value(User, "username", user.username)
    if username_check:
        return badresponse("Username already exists", 409)

    new_id = uuid5(UUID(UUID_SHA), user.username)
    new_user = {
        "id": new_id,
        "email": user.email,
        "name": user.name,
        "username": user.username,
        "hashed_password": Hasher.get_password_hash(user.password),
        "role": user.role,
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
        access_token=access_token,
        refresh_token=refresh_token,
    )
