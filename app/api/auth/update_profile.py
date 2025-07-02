from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.auth_schemas import UpdateProfile
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User


router = APIRouter()


@router.put("/update-profile")
async def upd_profile(user: Annotated[User, Depends(check_user)], update: UpdateProfile):
    if not user:
        return badresponse("Unauthorized", 401)

    updated_data = {}

    if update.name is not None:
        updated_data["name"] = update.name
    if update.username is not None:
        updated_data["username"] = update.username
    if update.description is not None:
        updated_data["description"] = update.description

    if not updated_data:
        return badresponse("No fields provided")

    await adapter.update_by_id(User, user.id, updated_data)
    return okresp
