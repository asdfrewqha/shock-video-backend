from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models.db_source.db_adapter import adapter
from models.hashing.passlib_hasher import Hasher
from models.schemas.auth_schemas import Tokens, UserLogin
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager

router = APIRouter()


@router.post("/token", response_model=Tokens,
             status_code=status.HTTP_201_CREATED)
async def token(user: UserLogin):

    bd_user = adapter.get_by_value(User, "username", user.username)

    if bd_user == []:
        return JSONResponse(
            content={"message": "Invalid credentials", "status": "error"},
            status_code=401,
        )

    bd_user = bd_user[0]

    if not Hasher.verify_password(user.password, bd_user.hashed_password):
        return JSONResponse(
            content={"message": "Invalid credentials", "status": "error"},
            status_code=401,
        )

    access_token = TokenManager.create_token(
        {"sub": str(bd_user.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = TokenManager.create_token(
        {"sub": str(bd_user.id), "type": "refresh"},
        TokenManager.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    tokens = Tokens(access_token=access_token, refresh_token=refresh_token)

    return tokens
