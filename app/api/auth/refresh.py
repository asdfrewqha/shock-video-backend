import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from app.core.dependencies import badresponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.token_manager import TokenManager


router = APIRouter()
Bear = HTTPBearer(auto_error=False)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_refresh(refresh_token: str = Security(Bear)):
    if not refresh_token or not refresh_token.credentials:
        logger.error("No token")
        return False

    data = TokenManager.decode_token(refresh_token.credentials)
    if not data:
        logger.error("No token data")
        return False

    if not data.get("sub") or not data.get("type"):
        logger.error("Invalid token data")
        return False

    if data["type"] != "refresh":
        logger.error("Invalid token type")
        return False

    user = await adapter.get_by_id(User, data["sub"])
    if user:
        return user

    logger.error("No user for this token")
    return False


@router.get("/refresh")
async def refresh(user: Annotated[User, Depends(check_refresh)]):
    if not user:
        return badresponse("Unauthorized", 401)

    new_access_token = TokenManager.create_token(
        {"sub": str(user.id), "type": "access"},
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return JSONResponse({"new_access_token": new_access_token})
