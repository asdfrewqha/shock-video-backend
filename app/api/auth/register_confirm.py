from fastapi import APIRouter
from uuid_v7.base import uuid7

from app.core.dependencies import badresponse
from app.models.auth_schemas import UserCreate, UserRegResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.db_source.redis_adapter import redis_adapter
from app.models.passlib_hasher import Hasher
from app.models.token_manager import TokenManager


router = APIRouter()


@router.post("/register-confirm/{code}", response_model=UserRegResponse, status_code=201)
async def confirm_registration(user: UserCreate, code: str):
    code_verify = await redis_adapter.get(f"email_verification_code:{user.email}")
    if not code_verify or code != code_verify:
        return badresponse("Code is invalid. Please, try again", 401)
    new_id = uuid7()
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

    return UserRegResponse(
        id=new_user_db.id,
        email=new_user_db.email,
        name=new_user_db.name,
        username=new_user_db.username,
        role=new_user_db.role,
        description=new_user_db.description,
        access_token=access_token,
    )
