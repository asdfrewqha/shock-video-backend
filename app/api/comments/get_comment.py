from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, CommentLike, User


router = APIRouter()


@router.get("/get-comment/{comment_id}")
async def get_comment(comment_id: UUID, user: Annotated[User, Depends(check_user)]):
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    if user:
        ex_like = await adapter.get_by_value(CommentLike, "user_id", user.id)
        if ex_like:
            liked = True if ex_like[0].like is True else False
            disliked = True if ex_like[0].like is False else False
        else:
            liked = False
            disliked = False
    else:
        liked = False
        disliked = False
    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "user_name": comment.user_name,
        "user_username": comment.user_username,
        "parent_username": comment.parent_username,
        "content": comment.content,
        "created_at": comment.created_at,
        "likes": comment.likes,
        "dislikes": comment.dislikes,
        "replies_count": comment.replies_count,
        "is_liked_by_user": liked,
        "is_disliked_by_user": disliked,
    }
