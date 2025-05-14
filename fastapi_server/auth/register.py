from fastapi import APIRouter, HTTPException, status
from models.db_source.sqlite_adapter import adapter
from models.tables.sqlite_tables import User
from models.schemas.auth import UserCreate, UserResponse
from fastapi.responses import JSONResponse
from models.hashing.passlib_hasher import Hasher
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):

    user_check = adapter.get_by_value(User, 'username', user.username)
    print(user_check)
    if user_check != []:
        return JSONResponse(content={"message": "Already exists"}, status_code=409)
    
    new_user = {
        'username':user.username,
        'hashed_password':Hasher.get_password_hash(user.password),
        'role':user.role
    }

    adapter.insert(User, new_user)

    new_user_db = adapter.get_by_value(User, 'username', user.username)[0]

    print(new_user_db)

    response_user = UserResponse(
        id=new_user_db.id,
        username=new_user_db.username,
        hashed_password=new_user_db.hashed_password,
        role=new_user_db.role
    )

    return response_user