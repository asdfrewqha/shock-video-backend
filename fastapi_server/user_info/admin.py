from fastapi import APIRouter, Security
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User
from models.schemas.auth_schemas import UserResponse
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from models.tokens.token_manager import TokenManager

router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/admin", response_model=UserResponse)
async def admin(access_token: str = Security(Bear)):

    data = TokenManager.decode_token(access_token.credentials)

    if "error" in data:
        return JSONResponse(
            content={"message": data["error"], "status": "error"}, status_code=401
        )
    if data["type"] != "access":
        return JSONResponse(
            content={"message": "Invalid token type", "status": "error"},
            status_code=401,
        )

    user_db = adapter.get_by_value(User, "username", data["username"])

    if user_db == []:
        return JSONResponse(
            content={"message": "Invalid token", "status": "error"}, status_code=401
        )

    user_db = user_db[0]

    if user_db.role != "ADMIN":
        return JSONResponse(
            content={"message": "Access denied", "status": "error"}, status_code=403
        )

    return {"details": "some message for admins"}
