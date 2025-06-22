from fastapi import APIRouter, UploadFile, File, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from config import SUPABASE_API, SUPABASE_URL
from uuid import uuid4
from supabase import create_client
from models.db_source.db_adapter import adapter
from models.tokens.token_manager import TokenManager
from models.tables.db_tables import Video, User
from moviepy.editor import VideoFileClip, AudioFileClip
import cv2
import tempfile
import os
import tqdm

router = APIRouter()

Bear = HTTPBearer(auto_error=False)


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
    dest_bitrate = int(40 * 1024 * 1024 * 8 / duration)  # in bits per second

    clip.write_videofile(
        output_path,
        codec="libx264",
        bitrate=f"{dest_bitrate}",
        audio_codec="aac",
        preset="ultrafast",
        fps=fps,
        threads=4
    )


def is_horizontal(video_path: str) -> bool:
    clip = VideoFileClip(video_path)
    width, height = clip.size

    if width >= height:
        return True
    else:
        return False


def gen_blur(input_path, target_resolution=(1080, 1920)):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        output_path = tmp.name
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    input_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    input_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm.tqdm(total=total_frames, desc="Blurring")
    out = cv2.VideoWriter(output_path,
                          cv2.VideoWriter_fourcc(*'mp4v'),
                          fps,
                          target_resolution)

    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        pbar.update(1)
        scale_w = target_resolution[0] / input_w
        scale_h = target_resolution[1] / input_h
        scale = min(scale_w, scale_h)
        new_w = int(input_w * scale)
        new_h = int(input_h * scale)
        resized_foreground = cv2.resize(frame, (new_w, new_h))
        bg = cv2.resize(frame, target_resolution)
        bg = cv2.GaussianBlur(bg, (99, 99), 30)
        x_offset = (target_resolution[0] - new_w) // 2
        y_offset = (target_resolution[1] - new_h) // 2
        composed_frame = bg.copy()
        composed_frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_foreground

        out.write(composed_frame)

    cap.release()
    out.release()
    print(f"Saved vertical video with blur to: {output_path}")

    video_clip = VideoFileClip(output_path)
    original_clip = VideoFileClip(input_path)
    if original_clip.audio:
        final_clip = video_clip.set_audio(original_clip.audio)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
    original_clip.close()
    return output_path


@router.post("/upload-video/")
async def upload_video(access_token: str = Security(Bear), file: UploadFile = File(...)):
    data = TokenManager.decode_token(access_token.credentials)

    if 'error' in data:
        return JSONResponse(content={"message": data['error'], "status": "error"}, status_code=401)
    if data['type'] != 'access':
        return JSONResponse(content={"message": "Invalid token type", "status": "error"}, status_code=401)

    user_db = adapter.get_by_value(User, 'username', data['username'])[0]
    if user_db == []:
        return JSONResponse(content={"message": "Invalid token", "status": "error"}, status_code=401)

    file_extension = file.filename.split(".")[-1]
    random_uuid = uuid4()
    filepath = f'{user_db.username}/{random_uuid}.{file_extension}'

    if file.content_type.startswith('video/'):
        output_path = ""
        inputp = ""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            input_path = tmp.name   
            file_size = os.path.getsize(input_path)
            if is_horizontal(input_path):
                print(1)
                inputp = gen_blur(input_path)
                if file_size < 50 * 1024 * 1024:
                    public_url = supabase_upd(file.content_type, filepath, inputp)
                else:
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_output:
                        output_path = tmp_output.name
                        print(2)
                        compress_video(inputp, output_path)
                        with open(output_path, "rb") as f:
                            public_url = supabase_upd("video/mp4", filepath, f)
                        tmp_output.close()
            else:
                if file_size < 50 * 1024 * 1024:
                    public_url = supabase_upd(file.content_type, filepath, input_path)
                else:
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_output:
                        output_path = tmp_output.name
                        print(2)
                        compress_video(input_path, output_path)
                        with open(output_path, "rb") as f:
                            public_url = supabase_upd("video/mp4", filepath, f)
                        tmp_output.close()
            tmp.close()
    print(3)
    new_video = {
        'id': str(random_uuid),
        'author_id': user_db.id,
        'url': public_url
        }
    adapter.insert(Video, new_video)
    await file.close()
    os.remove(input_path)
    if output_path: os.remove(output_path)
    if inputp: os.remove(inputp)
    return JSONResponse({"message": "success"}, status_code=201)
