from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import badresponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment


router = APIRouter()


@router.get("/get-comment-replies/{comment_id}")
async def get_comment_replies(comment_id: UUID):
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)

    replies = await adapter.get_replies(Comment, comment_id)

    return [
        {
            "id": reply.id,
            "user_id": reply.user_id,
            "content": reply.content,
            "created_at": reply.created_at,
            "likes": reply.likes,
            "dislikes": reply.dislikes,
        }
        for reply in replies
    ]
