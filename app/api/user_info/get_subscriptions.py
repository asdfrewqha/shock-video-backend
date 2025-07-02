from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Subscription, User


router = APIRouter()


@router.get("/get-subscriptions")
async def get_subscriptions(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    subscribes = await adapter.get_by_value(Subscription, "subscriber_id", user.id)
    list_subscribes = []
    for sub in subscribes:
        list_subscribes.append(str(sub.subscribed_to_id))
    return {"subscriptions": list_subscribes}
