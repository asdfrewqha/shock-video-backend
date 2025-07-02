from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User, View


router = APIRouter()


@router.get("/get-views")
async def get_views(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    views = await adapter.get_by_value(View, "user_id", user.id)
    views = [str(x.video_id) for x in views]
    return okresp(200, views)
