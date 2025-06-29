from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dependencies import check_user
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)

    response_user = UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        avatar_url=user.avatar_url,
    )

    return response_user
