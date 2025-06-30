from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from dependencies import badresponse, check_user, okresp
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/admin", response_model=UserResponse)
async def admin(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    elif user.role != "ADMIN":
        return badresponse("Forbidden", 403)
    return okresp(message="Admin")
