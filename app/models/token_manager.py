from datetime import datetime, timedelta
from typing import Any, Dict

from jose import JWTError, jwt

from app.core.config import RANDOM_SECRET


class TokenManager:
    SECRET_KEY = RANDOM_SECRET
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 60 дней

    @staticmethod
    def create_token(data: Dict[str, Any], expire_minutes: int = None) -> str:
        to_encode = data.copy()
        if expire_minutes is not None:
            expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        else:
            expire = datetime.utcnow() + timedelta(minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, TokenManager.SECRET_KEY, algorithm=TokenManager.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, TokenManager.SECRET_KEY, algorithms=[TokenManager.ALGORITHM]
            )

            if datetime.utcfromtimestamp(payload.get("exp")) < datetime.utcnow():
                return {"error": "Token has expired"}
            return payload
        except JWTError:
            return {"error": "Invalid token"}
