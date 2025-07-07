from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, User


router = APIRouter()


@router.put("/edit-comment/{comment_id}")
async def edit_comment(
    user: Annotated[User, Depends(check_user)],
    comment_id: UUID,
    content: str = Body(...),
):
    if not user:
        return badresponse("Unauthorized", 401)
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    if comment.user_id != user.id:
        return badresponse("Forbidden", 403)
    await adapter.update_by_id(Comment, comment_id, {"content": content})
    return okresp()
