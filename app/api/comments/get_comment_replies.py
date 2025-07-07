from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, CommentLike, User


router = APIRouter()


@router.get("/get-comment-replies/{comment_id}")
async def get_comment_replies(
    comment_id: UUID,
    user: Annotated[User, Depends(check_user)],
):
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)

    replies = await adapter.get_comment_replies(comment_id)
    if not replies:
        return []

    reply_ids = [r.id for r in replies]

    user_likes = {}
    if user:
        for uid in reply_ids:
            like = await adapter.get_by_values(
                CommentLike,
                and_conditions={"user_id": user.id},
                or_conditions={"comment_id": uid},
                mode="mixed",
            )
            if like:
                user_likes[like[0].comment_id] = like[0].like

    return [
        {
            "id": reply.id,
            "user_id": reply.user_id,
            "user_name": reply.user_name,
            "user_username": reply.user_username,
            "parent_username": reply.parent_username,
            "content": reply.content,
            "created_at": reply.created_at,
            "likes": reply.likes,
            "dislikes": reply.dislikes,
            "replies_count": reply.replies_count,
            "is_liked_by_user": user_likes.get(reply.id) is True,
            "is_disliked_by_user": user_likes.get(reply.id) is False,
        }
        for reply in replies
    ]
