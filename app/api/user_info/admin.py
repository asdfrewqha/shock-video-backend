from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_tables import User


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/admin")
async def admin(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    elif user.role != "ADMIN":
        return badresponse("Forbidden", 403)
    return okresp(message="Admin")
