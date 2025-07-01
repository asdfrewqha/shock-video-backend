import re

from fastapi import APIRouter, status

from app.core.dependencies import badresponse
from app.models.auth_schemas import Tokens, UserLogin
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.passlib_hasher import Hasher
from app.models.token_manager import TokenManager


router = APIRouter()


def is_valid_email(value: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, value))


def is_valid_username(value: str) -> bool:
    pattern = r"^[a-zA-Z0-9_]{3,}$"
    return bool(re.match(pattern, value))


@router.post("/token", response_model=Tokens, status_code=status.HTTP_201_CREATED)
async def token(user: UserLogin):
    if is_valid_email(user.identifier):
        bd_user = await adapter.get_by_value(User, "email", user.identifier)
    elif not is_valid_username(user.identifier):
        return badresponse("Username must be in Latin letters only")
    else:
        bd_user = await adapter.get_by_value(User, "username", f"@{user.identifier}")

    if bd_user == [] or bd_user is None:
        return badresponse("User not found", 404)

    bd_user = bd_user[0]

    if not Hasher.verify_password(user.password, bd_user.hashed_password):
        return badresponse("Forbidden", 403)

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
