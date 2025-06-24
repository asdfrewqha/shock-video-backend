import gc
import logging
import mimetypes
import os
import tempfile
import time
from uuid import UUID

import cv2
from fastapi import APIRouter, File, Form, Security, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from moviepy.editor import VideoFileClip
from supabase import create_client
from uuid_v7.base import uuid7

from config import SUPABASE_API, SUPABASE_URL
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User, Video
from models.tokens.token_manager import TokenManager


mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("video/quicktime", ".mov")
mimetypes.add_type("video/webm", ".webm")

router = APIRouter()
Bear = HTTPBearer(auto_error=False)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

supabase = create_client(SUPABASE_URL, SUPABASE_API)
bucket = supabase.storage.from_("videos")

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
    ".avi",
    ".mkv",
    ".flv",
    ".wmv",
    ".m4v",  # video
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",  # image
}


def supabase_upd(content_type, filepath, file_data):
    bucket.upload(
        path=filepath,
        file=file_data,
        file_options={
            "content-type": content_type})
    return bucket.get_public_url(filepath)


def compress_video(input_path, output_path):
    clip = VideoFileClip(input_path)
    try:
        duration = clip.duration
        bitrate = int((50 * 1024 * 1024 * 8) / duration)
        clip.write_videofile(
            output_path,
            codec="libx264",
            bitrate=str(bitrate),
            audio_codec="aac",
            preset="ultrafast",
            fps=clip.fps or 24,
        )
    finally:
        clip.close()


def is_horizontal(video_path):
    clip = VideoFileClip(video_path)
    try:
        width, height = clip.size
        return width >= height
    finally:
        clip.close()


def gen_blur(input_path, target_resolution=(1080, 1920)):
    output_width, output_height = target_resolution
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    clip = VideoFileClip(input_path)
    try:
        width, height = clip.size
        scale_fg = min(output_width / width, output_height / height)
        scale_bg = max(output_width / width, output_height / height)

        def process_frame(frame):
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            resized = cv2.resize(
                frame_bgr, (int(width * scale_fg), int(height * scale_fg))
            )
            background = cv2.resize(
                frame_bgr, (int(width * scale_bg), int(height * scale_bg))
            )
            y = (background.shape[0] - output_height) // 2
            x = (background.shape[1] - output_width) // 2
            background = background[y: y + output_height, x: x + output_width]
            small = cv2.resize(
                background, (output_width // 4, output_height // 4))
            blurred = cv2.resize(
                cv2.GaussianBlur(
                    small, (25, 25), 0), (output_width, output_height))
            x_offset = (output_width - resized.shape[1]) // 2
            y_offset = (output_height - resized.shape[0]) // 2
            blurred[
                y_offset: y_offset + resized.shape[0],
                x_offset: x_offset + resized.shape[1],
            ] = resized
            return cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

        processed = clip.fl_image(process_frame)
        if clip.audio:
            processed = processed.set_audio(clip.audio)

        bitrate = (15 * 1024 * 1024 * 8) / clip.duration
        processed.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            fps=clip.fps or 24,
            bitrate=str(bitrate),
        )
        return output_path
    finally:
        clip.close()
        if "processed" in locals():
            processed.close()


@router.post("/upload-video/")
async def upload_video(
    access_token: str = Security(Bear),
    file: UploadFile = File(...),
    description: str = Form(""),
):
    if not access_token or not access_token.credentials:
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )
    data = TokenManager.decode_token(access_token.credentials)
    if "error" in data or data["type"] != "access":
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )

    user_db = adapter.get_by_id(User, UUID(data["sub"]))
    if not user_db:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )

    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            {"message": "Unsupported file extension"}, status_code=400)

    mime_type = mimetypes.guess_type(file.filename)[0]
    if not mime_type or mime_type == "application/octet-stream":
        mime_type = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".webp": "image/webp",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }.get(ext, "application/octet-stream")

    random_uuid = uuid7()
    filepath = f"{user_db.username}/{random_uuid}{ext}"
    public_url = None
    input_path = output_path = inputp = None

    try:
        content = await file.read()
        await file.close()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            input_path = tmp.name

        size = os.path.getsize(input_path)
        logger.info(
            f"Uploading file: {file.filename}, Size: {size}, Mime: {mime_type}, User: {user_db.username}" # noqa
        )

        if mime_type.startswith("video/"):
            if is_horizontal(input_path):
                logger.info(
                    "Horizontal video — generating blurred background.")
                inputp = gen_blur(input_path)
                with open(inputp, "rb") as f:
                    public_url = supabase_upd("video/mp4", filepath, f)
            elif size < 50 * 1024 * 1024:
                logger.info("Uploading vertical video without compression.")
                public_url = supabase_upd(mime_type, filepath, content)
            else:
                logger.info("Compressing vertical video before upload.")
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out:
                    output_path = out.name
                    compress_video(input_path, output_path)
                    with open(output_path, "rb") as f:
                        public_url = supabase_upd("video/mp4", filepath, f)

        elif mime_type.startswith("image/"):
            logger.info("Uploading image file.")
            public_url = supabase_upd(mime_type, filepath, content)
        else:
            return JSONResponse(
                {"message": "Unsupported file type"}, status_code=400)

        if not public_url:
            return JSONResponse({"message": "Upload failed"}, status_code=500)

        logger.info(f"File uploaded successfully: {public_url}")
        adapter.insert(
            Video,
            {
                "id": str(random_uuid),
                "author_id": user_db.id,
                "url": public_url,
                "description": description,
            },
        )
        return JSONResponse(
            {"message": "success", "url": public_url}, status_code=201)

    finally:
        for path in [input_path, output_path, inputp]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    time.sleep(0.5)
                    gc.collect()
                    try:
                        os.remove(path)
                    except Exception:
                        logger.warning(f"Could not remove file: {path}")
