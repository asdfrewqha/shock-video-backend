import logging
import secrets
import string

from fastapi import APIRouter

from app.api.auth.tasks import send_confirmation_email
from app.core.dependencies import badresponse, okresp
from app.models.auth_schemas import UserCreate
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.db_source.redis_adapter import redis_adapter


router = APIRouter()
logger = logging.getLogger(__name__)


def generate_secure_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post("/register")
async def register(user: UserCreate):
    email_check = await adapter.get_by_value(User, "email", user.email)
    if email_check:
        return badresponse("Email already exists", 409)
    username_check = await adapter.get_by_value(User, "username", user.username)
    if username_check:
        return badresponse("Username already exists", 409)
    random_code = generate_secure_code()
    await redis_adapter.set(f"email_verification_code:{user.email}", random_code, expire=600)
    send_confirmation_email.delay(user.email, random_code)
    return okresp(200, "Code sent succesfully")
