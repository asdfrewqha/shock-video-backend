from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.dependencies import badresponse, check_refresh
from app.models.db_source.db_tables import User
from app.models.token_manager import TokenManager


router = APIRouter()


@router.get("/refresh")
async def refresh(user: Annotated[User, Depends(check_refresh)]):
    if not user:
        return badresponse("Unauthorized", 401)

    new_access_token = TokenManager.create_token(
        {"sub": str(user.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return JSONResponse({"new_access_token": new_access_token})
