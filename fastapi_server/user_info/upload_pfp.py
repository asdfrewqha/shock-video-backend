import asyncio
import io
import tempfile
import os
import logging
from typing import Annotated

from PIL import Image
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse, Response
from supabase import create_client

from config import SUPABASE_API, SUPABASE_URL
from dependencies import check_user
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User


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


async def supabase_upload_async(filepath: str, image_bytes: bytes):
    loop = asyncio.get_running_loop()

    def upload():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        try:
            bucket.upload(
                path=filepath,
                file=tmp_path,
                file_options={"content-type": "image/png"},
            )
            return bucket.get_public_url(filepath)
        finally:
            os.remove(tmp_path)

    return await loop.run_in_executor(None, upload)


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
    if not user:
        return JSONResponse({"message": "Invalid token", "status": "error"}, status_code=401)

    if user.avatar_url:
        return JSONResponse(
            {"message": "You have an avatar. If you want to change it - use other methods"},
            status_code=409,
        )

    filename = f"{user.username}/avatar_{user.id}.png"
    logger.info("Uploading pfp")
    try:
        img = Image.open(file.file).convert("RGBA")
        img = center_crop(img)
        img = img.resize((512, 512))

        with io.BytesIO() as output:
            img.save(output, format="PNG")
            image_bytes = output.getvalue()
        public_url = await supabase_upload_async(filename, image_bytes)

        await adapter.update_by_id(User, user.id, {"avatar_url": public_url})

        return JSONResponse({"message": "Profile picture uploaded", "url": public_url}, status_code=201)

    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        return JSONResponse({"message": "Upload failed"}, status_code=500)


@router.put("/profile-picture")
async def updt_pfp(
    user: Annotated[User, Depends(check_user)],
    file: UploadFile = File(...),
):
    if not user:
        return JSONResponse({"message": "Invalid token", "status": "error"}, status_code=401)

    filename = f"{user.username}/avatar_{user.id}.png"
    logger.info("Uploading pfp")
    try:
        img = Image.open(file.file).convert("RGBA")
        img = center_crop(img)
        img = img.resize((512, 512))

        with io.BytesIO() as output:
            img.save(output, format="PNG")
            image_bytes = output.getvalue()

        try:
            await supabase_remove_async(filename)
        except Exception as e:
            logger.warning(f"Failed to remove old avatar: {e}")

        public_url = await supabase_upload_async(filename, image_bytes)

        await adapter.update_by_id(User, user.id, {"avatar_url": public_url})

        return JSONResponse({"message": "Profile picture updated", "url": public_url}, status_code=200)

    except Exception as e:
        logger.error(f"Error updating profile picture: {e}")
        return JSONResponse({"message": "Update failed"}, status_code=500)


@router.delete("/profile-picture", status_code=204)
async def del_pfp(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse({"message": "Invalid token", "status": "error"}, status_code=401)

    if not user.avatar_url:
        return JSONResponse({"message": "You don't have any avatars"}, status_code=404)

    filename = f"{user.username}/avatar_{user.id}.png"

    try:
        await supabase_remove_async(filename)
        await adapter.update_by_id(User, user.id, {"avatar_url": None})
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        return JSONResponse({"message": "Delete failed"}, status_code=500)

    return Response(status_code=204)
