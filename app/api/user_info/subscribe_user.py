from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Subscription, User


router = APIRouter()


@router.post("/subscribe/{uuid}")
async def subscribe(user: Annotated[User, Depends(check_user)], uuid: UUID):
    if not user:
        return badresponse("Unauthorized", 401)
    user_db = await adapter.get_by_id(User, uuid)
    if not user_db:
        return badresponse("User not found", 404)
    ex_subscription = await adapter.get_by_values(
        Subscription,
        {
            "subscriber_id": user.id,
            "subscribed_to_id": uuid,
        },
    )
    if ex_subscription:
        ex_subscription = ex_subscription[0]
        await adapter.delete(Subscription, ex_subscription.id)
        await adapter.update_by_id(
            User, uuid, {"followers_count": max(user_db.followers_count - 1, 0)}
        )
        await adapter.update_by_id(
            User, user.id, {"subscriptions_count": max(user.subscriptions_count - 1, 0)}
        )
        return Response(status_code=204)
    await adapter.insert(
        Subscription,
        {
            "subscriber_id": user.id,
            "subscribed_to_id": uuid,
        },
    )
    await adapter.update_by_id(User, uuid, {"followers_count": user_db.followers_count + 1})
    await adapter.update_by_id(User, user.id, {"subscriptions_count": user.subscriptions_count + 1})
    return okresp(message="Subscribed succesfully")
