from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from dependencies import check_user
from fastapi_server.video.delete_video import extract_uuid_from_url
from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoModel
from models.tables.db_tables import Like, User, Video


router = APIRouter()


@router.post("/like-video")
async def like_video(
    video: VideoModel,
    user: Annotated[User, Depends(check_user)],
    like: bool = Query(True)
):
    if video.uuid:
        video_id = video.uuid
    elif video.url:
        video_id = extract_uuid_from_url(video.url)
        if not video_id:
            return JSONResponse(
                content={
                    "message": "Invalid request. Video not specified",
                    "status": "error",
                },
                status_code=400,
            )
    else:
        return JSONResponse(
            content={
                "message": "Invalid request. Video not specified",
                "status": "error",
            },
            status_code=400,
        )
    if not user:
        return JSONResponse(
            content={
                "message": "Invalid user",
                "status": "error"},
            status_code=401)

    video = await adapter.get_by_id(Video, video_id)
    if not video:
        return JSONResponse(
            content={
                "message": "Video not found",
                "status": "error"},
            status_code=404)

    existing_like = await adapter.get_by_values(
        Like, {"user_id": user.id, "video_id": video_id}
    )

    if existing_like:
        prev_like = existing_like[0]
        await adapter.delete(Like, prev_like.id)

        if prev_like.like:
            video.likes = max(video.likes - 1, 0)
        else:
            video.dislikes = max(video.dislikes - 1, 0)

        if prev_like.like == like:
            await adapter.update(
                Video,
                {"likes": video.likes, "dislikes": video.dislikes},
                video_id
            )
            return JSONResponse(
                content={
                    "message": f"Video un{'liked' if like else 'disliked'} successfully"
                }
            )

    await adapter.insert(Like,
                         {"user_id": user.id,
                          "video_id": video_id,
                          "like": like})

    if like:
        video.likes += 1
    else:
        video.dislikes += 1

    await adapter.update(Video, {"likes": video.likes,
                                 "dislikes": video.dislikes}, video_id)

    return JSONResponse(
        content={
            "message": f"Video {'liked' if like else 'disliked'} successfully"
        })
