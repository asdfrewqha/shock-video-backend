from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, CommentLike, User, Video


router = APIRouter()


@router.get("/get-comments/{video_id}")
async def get_comments(video_id: UUID, user: Annotated[User, Depends(check_user)]):
    video = await adapter.get_by_id(Video, video_id)
    if not video:
        return badresponse("Video not found", 404)
    root_comments = await adapter.get_by_values(Comment, {"video_id": video_id, "parent_id": None})
    if not root_comments:
        return []
    comment_ids = [c.id for c in root_comments]
    user_likes = {}
    if user:
        for uid in comment_ids:
            like = await adapter.get_by_values(
                CommentLike,
                and_conditions={"user_id": user.id},
                or_conditions={"comment_id": uid},
                mode="mixed",
            )
            if like:
                user_likes[like[0].comment_id] = like[0].like
    result = []
    for c in root_comments:
        liked = user_likes.get(c.id) is True
        disliked = user_likes.get(c.id) is False
        result.append(
            {
                "id": c.id,
                "user_id": c.user_id,
                "user_name": c.user_name,
                "user_username": c.user_username,
                "content": c.content,
                "created_at": c.created_at,
                "likes": c.likes,
                "dislikes": c.dislikes,
                "is_liked_by_user": liked,
                "is_disliked_by_user": disliked,
            }
        )
    return result
