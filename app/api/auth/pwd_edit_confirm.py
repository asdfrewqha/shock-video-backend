from fastapi import APIRouter
from itsdangerous import BadSignature
from itsdangerous.url_safe import URLSafeTimedSerializer

from app.core.dependencies import badresponse, okresp
from app.models.auth_schemas import EditPwdRequest
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User
from app.models.passlib_hasher import Hasher


router = APIRouter()


@router.put("/edit-password-confirm/{token}")
async def edit_pwd_confirm(token: str, password: EditPwdRequest):
    serializer = URLSafeTimedSerializer()
    try:
        user_id = serializer.loads(token, max_age=600)
    except BadSignature:
        return badresponse("Token is invalid or has expired")
    user = await adapter.get_by_id(User, user_id)
    if not user:
        return badresponse("User with this token does not exist")
    if Hasher.verify_password(password.password, user.password_hash):
        return badresponse("Your password is the same with the old one")
    password_hash = Hasher.get_password_hash(password=password.password)
    await adapter.update_by_id(User, user_id, {"password_hash": password_hash})
    return okresp(200, "Password changed succesfully")
