from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Dict, Any

class TokenManager:
    SECRET_KEY = "your_secret_key"  # Замените на ваш секретный ключ
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 60 дней

    @staticmethod
    def create_access_token(data: Dict[str, Any], expire_minutes: int = None) -> str:
        """Создает JWT токен с данными пользователя, принимая время истечения в минутах."""
        to_encode = data.copy()
        if expire_minutes is not None:
            expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        else:
            expire = datetime.utcnow() + timedelta(minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, TokenManager.SECRET_KEY, algorithm=TokenManager.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Dict[str, Any]:
        """Декодирует JWT токен и возвращает данные, если токен действителен."""
        try:
            payload = jwt.decode(token, TokenManager.SECRET_KEY, algorithms=[TokenManager.ALGORITHM])
            # Проверка на истечение срока действия токена
            if datetime.utcfromtimestamp(payload.get("exp")) < datetime.utcnow():
                return {"error": "Token has expired"}
            return payload
        except JWTError:
            return {"error": "Invalid token"}
