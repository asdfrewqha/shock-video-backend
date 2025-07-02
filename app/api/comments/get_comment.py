from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import badresponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment


router = APIRouter()


@router.get("/get-comment/{comment_id}")
async def get_comment(comment_id: UUID):
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "likes": comment.likes,
        "dislikes": comment.dislikes,
    }
