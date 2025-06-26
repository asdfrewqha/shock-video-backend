from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dependencies import check_refresh
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager


router = APIRouter()


@router.get("/refresh")
async def refresh(user: Annotated[User, Depends(check_refresh)]):
    if not user:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)

    new_access_token = TokenManager.create_token(
        {"sub": str(user.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return {"new_access_token": new_access_token}
