from uuid import UUID

from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/me", response_model=UserResponse)
async def me(access_token: str = Security(Bear)):

    data = TokenManager.decode_token(access_token.credentials)

    if "error" in data:
        return JSONResponse(
            content={
                "message": data["error"],
                "status": "error"},
            status_code=401)
    if data["type"] != "access":
        return JSONResponse(
            content={"message": "Invalid token type", "status": "error"},
            status_code=401,
        )

    user_db = adapter.get_by_id(User, UUID(data["sub"]))

    if not user_db:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)

    response_user = UserResponse(
        id=user_db.id,
        username=user_db.username,
        role=user_db.role,
        avatar_url=user_db.avatar_url,
    )

    return response_user
