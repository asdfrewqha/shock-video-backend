import logging

from fastapi import Security
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.tables.db_tables import User
from models.tokens.token_manager import TokenManager


Bear = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_user(access_token: str = Security(Bear)):
    if not access_token or not access_token.credentials:
        logger.error("No token")
        return False
    data = TokenManager.decode_token(access_token.credentials)
    if not data:
        logger.error("No token data")
        return False
    elif not data.get("sub") or not data.get("type"):
        logger.error("Invalid token data")
        return False
    elif data["type"] != "access":
        logger.error("Invalid token type")
        return False
    else:
        user = adapter.get_by_id(User, data["sub"])
        if user:
            return user
        else:
            logger.error("No user for this token")
            return False


async def check_refresh(refresh_token: str = Security(Bear)):
    if not refresh_token or not refresh_token.credentials:
        logger.error("No token")
        return False
    data = TokenManager.decode_token(refresh_token.credentials)
    if not data:
        logger.error("No token data")
        return False
    elif not data.get("sub") or not data.get("type"):
        logger.error("Invalid token data")
        return False
    elif data["type"] != "refresh":
        logger.error("Invalid token type")
        return False
    else:
        user = adapter.get_by_id(User, data["sub"])
        if user:
            return user
        else:
            logger.error("No user for this token")
            return False
