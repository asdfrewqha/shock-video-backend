from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from dependencies import check_user
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/admin", response_model=UserResponse)
async def admin(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)
    elif user.role != "ADMIN":
        return JSONResponse(
            content={
                "message": "Access denied",
                "status": "error"},
            status_code=403)

    return {"details": "some message for admins"}
