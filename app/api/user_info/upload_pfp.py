import asyncio
import io
import logging
from typing import Annotated

from PIL import Image
from fastapi import APIRouter, Depends, File, UploadFile
from supabase import create_client

from app.core.config import DEFAULT_AVATAR_URL, SUPABASE_API, SUPABASE_URL
from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

supabase = create_client(SUPABASE_URL, SUPABASE_API)
bucket = supabase.storage.from_("pfps")


def center_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    return image.crop((left, top, right, bottom))


async def supabase_remove_async(filepath: str):
    loop = asyncio.get_running_loop()

    def remove():
        return bucket.remove(paths=[filepath])

    return await loop.run_in_executor(None, remove)


@router.post("/profile-picture")
async def upld_pfp(
    user: Annotated[User, Depends(check_user)],
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        return badresponse("Unsupported file", 415)
    if not user:
        return badresponse("Unauthorized", 401)

    if user.avatar_url != DEFAULT_AVATAR_URL:
        return badresponse("Already exists", 409)

    filename = f"{user.username}/avatar_{user.id}.png"
    logger.info("Uploading pfp")
    img = Image.open(file.file).convert("RGB")
    img = center_crop(img)
    img = img.resize((512, 512))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    bucket.upload(filename, buffer.getvalue(), {"content-type": "image/png"})
    public_url = bucket.get_public_url(filename)
    await adapter.update_by_id(User, user.id, {"avatar_url": public_url})

    return okresp(201, "Uploaded")


@router.put("/profile-picture")
async def updt_pfp(
    user: Annotated[User, Depends(check_user)],
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        return badresponse("Unsupported file", 415)
    if not user:
        return badresponse("Unauthorized", 401)
    filename = f"{user.username}/avatar_{user.id}.png"
    logger.info("Uploading pfp")
    img = Image.open(file.file).convert("RGB")
    img = center_crop(img)
    img = img.resize((512, 512))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    try:
        await supabase_remove_async(filename)
    except Exception as e:
        return badresponse(f"Failed to remove old avatar: {e}", 500)
    bucket.upload(filename, buffer.getvalue(), {"content-type": "image/png"})
    public_url = bucket.get_public_url(filename)
    await adapter.update_by_id(User, user.id, {"avatar_url": public_url})

    return okresp(200, "Updated")


@router.delete("/profile-picture", status_code=204)
async def del_pfp(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)

    if not user.avatar_url:
        return badresponse("Not found", 404)

    filename = f"{user.username}/avatar_{user.id}.png"

    try:
        await supabase_remove_async(filename)
        await adapter.update_by_id(User, user.id, {"avatar_url": DEFAULT_AVATAR_URL})
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        return badresponse(f"Error deleting old avatar: {e}", 500)

    return okresp(204)
