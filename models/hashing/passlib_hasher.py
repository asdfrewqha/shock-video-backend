from passlib.context import CryptContext

# Создаем контекст для хеширования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Создает хеш пароля."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли введенный пароль хешу."""
        return pwd_context.verify(plain_password, hashed_password)
