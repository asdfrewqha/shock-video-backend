from uuid import UUID, uuid5

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from config import UUID_SHA
from models.db_source.db_adapter import adapter
from models.hashing.passlib_hasher import Hasher
from models.schemas.auth_schemas import UserCreate, UserResponse
from models.tables.db_tables import User


router = APIRouter()


@router.post("/register", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    user_check = adapter.get_by_value(User, "username", user.username)

    if user_check != []:
        return JSONResponse(
            content={
                "message": "Already exists"},
            status_code=409)
    new_id = uuid5(UUID(UUID_SHA), user.username)
    new_user = {
        "id": new_id,
        "username": user.username,
        "hashed_password": Hasher.get_password_hash(user.password),
        "role": user.role,
    }

    adapter.insert(User, new_user)

    new_user_db = adapter.get_by_value(User, "username", user.username)[0]

    response_user = UserResponse(
        id=new_user_db.id, username=new_user_db.username, role=new_user_db.role
    )

    return response_user
