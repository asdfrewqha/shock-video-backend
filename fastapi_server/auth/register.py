from uuid import UUID, uuid5

from fastapi import APIRouter, status

from config import UUID_SHA
from dependencies import badresponse
from models.db_source.db_adapter import adapter
from models.hashing.passlib_hasher import Hasher
from models.schemas.auth_schemas import UserCreate, UserResponse
from models.tables.db_tables import User


router = APIRouter()

@router.post("/register", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    user_check = await adapter.get_by_value(User, "username", user.username)

    if user_check:
        return badresponse("Already exists", 409)

    new_id = uuid5(UUID(UUID_SHA), user.username)
    new_user = {
        "id": new_id,
        "username": user.username,
        "hashed_password": Hasher.get_password_hash(user.password),
        "role": user.role,
    }

    await adapter.insert(User, new_user)

    new_user_db = await adapter.get_by_value(User, "username", user.username)
    user_instance = new_user_db[0]

    return UserResponse(
        id=user_instance.id,
        username=user_instance.username,
        role=user_instance.role
    )
