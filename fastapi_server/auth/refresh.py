from uuid import UUID

from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/refresh")
async def refresh(refresh_token: str = Security(Bear)):
    if not refresh_token or refresh_token.credentials:
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )
    data = TokenManager.decode_token(refresh_token.credentials)
    if "error" in data:
        return JSONResponse(
            content={
                "message": data["error"],
                "status": "error"},
            status_code=401)
    if data["type"] != "refresh":
        return JSONResponse(
            content={"message": "Invalid token type", "status": "error"},
            status_code=401,
        )

    user_db = adapter.get_by_id(User, UUID(data["sub"]))

    if user_db == []:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)

    new_access_token = TokenManager.create_token(
        {"sub": data["sub"], "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return {"new_access_token": new_access_token}
