from fastapi import APIRouter, UploadFile, File, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from config import SUPABASE_API, SUPABASE_URL
from uuid import uuid4
from supabase import create_client
from models.db_source.db_adapter import adapter
from models.tokens.token_manager import TokenManager
from models.tables.db_tables import Video, User
from moviepy.editor import VideoFileClip
import tempfile
import logging
import cv2
import os
import gc

router = APIRouter()
Bear = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def supabase_upd(content_type, filepath, contents):
    supabase = create_client(SUPABASE_URL, SUPABASE_API)
    bucket_name = "videos"
    supabase.storage.from_(bucket_name).upload(
        path=filepath,
        file=contents,
        file_options={"content-type": content_type}
    )
    public_url = supabase.storage.from_(bucket_name).get_public_url(filepath)
    return public_url

def compress_video(input_path, output_path):
    clip = VideoFileClip(input_path)
    fps = clip.fps if isinstance(clip.fps, (int, float)) else 24
    duration = clip.duration
    dest_bitrate = int(40 * 1024 * 1024 * 8 / duration)
    clip.write_videofile(
        output_path,
        codec="libx264",
        bitrate=f"{dest_bitrate}",
        audio_codec="aac",
        preset="ultrafast",
        fps=fps,
        threads=4
    )
    clip.close()

def is_horizontal(video_path: str) -> bool:
    clip = VideoFileClip(video_path)
    width, height = clip.size
    result = width >= height
    clip.close()
    return result

def gen_blur(input_path, target_resolution=(1080, 1920)):
    output_width, output_height = target_resolution
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name

    clip = VideoFileClip(input_path)
    width, height = clip.size
    scale_fg = min(output_width / width, output_height / height)
    scale_bg = max(output_width / width, output_height / height)

    def process_frame(frame):
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        resized = cv2.resize(frame_bgr, (int(width * scale_fg), int(height * scale_fg)))
        background = cv2.resize(frame_bgr, (int(width * scale_bg), int(height * scale_bg)))
        y_start = (background.shape[0] - output_height) // 2
        x_start = (background.shape[1] - output_width) // 2
        background_cropped = background[y_start:y_start + output_height, x_start:x_start + output_width]
        small_bg = cv2.resize(background_cropped, (int(output_width * 0.25), int(output_height * 0.25)))
        blurred_small = cv2.GaussianBlur(small_bg, (25, 25), 0)
        blurred = cv2.resize(blurred_small, (output_width, output_height), interpolation=cv2.INTER_LINEAR)
        new_w, new_h = resized.shape[1], resized.shape[0]
        x_offset = (output_width - new_w) // 2
        y_offset = (output_height - new_h) // 2
        blurred[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        return cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

    processed_clip = clip.fl_image(process_frame)
    if clip.audio:
        processed_clip = processed_clip.set_audio(clip.audio)

    fps = clip.fps or 24
    bitrate = int(40 * 1024 * 1024 * 8 / clip.duration) if os.path.getsize(input_path) > 50 * 1024 * 1024 else None

    processed_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        fps=fps,
        bitrate=f"{bitrate}" if bitrate else None
    )
    clip.close()
    processed_clip.close()
    return output_path

@router.post("/upload-video/")
async def upload_video(access_token: str = Security(Bear), file: UploadFile = File(...)):
    data = TokenManager.decode_token(access_token.credentials)

    if 'error' in data:
        return JSONResponse(content={"message": data['error'], "status": "error"}, status_code=401)
    if data['type'] != 'access':
        return JSONResponse(content={"message": "Invalid token type", "status": "error"}, status_code=401)

    user_result = adapter.get_by_value(User, 'username', data['username'])
    if not user_result:
        return JSONResponse(content={"message": "Invalid token", "status": "error"}, status_code=401)

    user_db = user_result[0]
    file_extension = file.filename.split(".")[-1]
    random_uuid = uuid4()
    filepath = f'{user_db.username}/{random_uuid}.{file_extension}'

    public_url = None
    input_path = output_path = inputp = None

    try:
        if file.content_type.startswith('video/'):
            content = await file.read()
            await file.close()
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                input_path = tmp.name

            file_size = os.path.getsize(input_path)

            if is_horizontal(input_path):
                logger.info(f"Processing horizontal video for user {user_db.username}")
                inputp = gen_blur(input_path)
                public_url = supabase_upd("video/mp4", filepath, inputp)
            elif file_size < 50 * 1024 * 1024:
                logger.info(f"Uploading small vertical video for user {user_db.username}")
                public_url = supabase_upd(file.content_type, filepath, input_path)
            else:
                logger.info(f"Compressing large vertical video for user {user_db.username}")
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_output:
                    output_path = tmp_output.name
                    compress_video(input_path, output_path)
                    with open(output_path, "rb") as f:
                        public_url = supabase_upd("video/mp4", filepath, f)

        if not public_url:
            logger.error("Video processing failed — no public URL")
            return JSONResponse(content={"message": "Failed to process video", "status": "error"}, status_code=500)

        new_video = {
            'id': str(random_uuid),
            'author_id': user_db.id,
            'url': public_url
        }
        adapter.insert(Video, new_video)
        logger.info(f"Video {random_uuid} uploaded successfully by user {user_db.username}")
        return JSONResponse({"message": "success"}, status_code=201)

    finally:
        for path in [input_path, output_path, inputp]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    gc.collect()
                    try:
                        os.remove(path)
                    except Exception:
                        logger.warning(f"Couldn't delete temp file: {path}")
