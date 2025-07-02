from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, CommentLike, User


router = APIRouter()


@router.post("/like-comment/{comment_id}")
async def like_comment(
    user: Annotated[User, Depends(check_user)], comment_id: UUID, like: bool = True
):
    if not user:
        return badresponse("Unauthorized", 401)
    comment = await adapter.get_by_id(Comment, comment_id)
    if not comment:
        return badresponse("Comment not found", 404)
    existing_like = await adapter.get_by_values(
        CommentLike, {"user_id": user.id, "comment_id": comment_id}
    )

    if existing_like:
        prev_like = existing_like[0]
        await adapter.delete(CommentLike, prev_like.id)

        if prev_like.like:
            comment.likes = max(comment.likes - 1, 0)
        else:
            comment.dislikes = max(comment.dislikes - 1, 0)

        if prev_like.like == like:
            await adapter.update_by_id(
                Comment, comment_id, {"likes": comment.likes, "dislikes": comment.dislikes}
            )
            return okresp(message=f"{'liked' if like else 'disliked'}")

    await adapter.insert(CommentLike, {"user_id": user.id, "comment_id": comment_id, "like": like})

    if like:
        comment.likes += 1
    else:
        comment.dislikes += 1

    await adapter.update_by_id(
        Comment, comment_id, {"likes": comment.likes, "dislikes": comment.dislikes}
    )

    return okresp(message=f"{'liked' if like else 'disliked'}")
