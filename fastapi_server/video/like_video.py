from fastapi import APIRouter, Security, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video, User, Like
from models.tokens.token_manager import TokenManager
from fastapi_server.video.delete_video import extract_uuid_from_url

router = APIRouter()
Bear = HTTPBearer(auto_error=False)


@router.post("/like-video")
async def like_video(
    uuid: str = Form(None),
    url: str = Form(None),
    like: bool = True,
    access_token: str = Security(Bear),
):
    data = TokenManager.decode_token(access_token.credentials)

    if uuid:
        video_id = uuid
    elif url:
        video_id = extract_uuid_from_url(url)
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

    if "error" in data or data.get("type") != "access":
        return JSONResponse(
            content={"message": "Invalid token", "status": "error"}, status_code=401
        )

    user = adapter.get_by_value(User, "username", data["username"])
    if not user:
        return JSONResponse(
            content={"message": "Invalid user", "status": "error"}, status_code=401
        )
    user_id = user[0].id

    video = adapter.get_by_value(Video, "id", video_id)
    if not video:
        return JSONResponse(
            content={"message": "Video not found", "status": "error"}, status_code=404
        )
    video_db = video[0]

    existing_like = adapter.get_by_values(
        Like, {"user_id": user_id, "video_id": video_id}
    )

    if existing_like:
        prev_like = existing_like[0]
        adapter.delete(Like, prev_like.id)

        if prev_like.like:
            video_db.likes = max(video_db.likes - 1, 0)
        else:
            video_db.dislikes = max(video_db.dislikes - 1, 0)

        if prev_like.like == like:
            adapter.update(
                Video,
                {"likes": video_db.likes, "dislikes": video_db.dislikes},
                video_id,
            )
            return JSONResponse(
                content={
                    "message": f"Video un{'liked' if like else 'disliked'} successfully"
                }
            )

    adapter.insert(Like, {"user_id": user_id, "video_id": video_id, "like": like})
    if like:
        video_db.likes += 1
    else:
        video_db.dislikes += 1

    adapter.update(
        Video, {"likes": video_db.likes, "dislikes": video_db.dislikes}, video_id
    )
    return JSONResponse(
        content={"message": f"Video {'liked' if like else 'disliked'} successfully"}
    )
