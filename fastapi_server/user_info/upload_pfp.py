import os
import tempfile
from typing import Annotated

from dependencies import check_user
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from supabase import create_client

from config import SUPABASE_API, SUPABASE_URL
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User


router = APIRouter()

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


@router.post("/profile-picture")
async def upld_pfp(
        user: Annotated[User, Depends(check_user)],
        file: UploadFile = File(...)):
    if not user:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    if user.avatar_url:
        return JSONResponse(
            content={
                "message": "You have an avatar. If you want to change it - use other methods"
            },
            status_code=409,
        )
    filename = f"{user.username}/avatar_{user.id}.png"
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        with Image.open(file.file) as img:
            img = img.convert("RGBA")
            img = center_crop(img)
            img = img.resize((512, 512))
            img.save(tmp_path, format="PNG")
        with open(tmp_path, "rb") as f:
            bucket.upload(
                path=filename, file=f, file_options={
                    "content-type": "image/png"})
        public_url = bucket.get_public_url(filename)
        adapter.update_by_id(User, user.id, {"avatar_url": public_url})
        return JSONResponse(
            {"message": "Profile picture uploaded", "url": public_url}, status_code=201
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.put("/profile-picture")
async def updt_pfp(
        user: Annotated[User, Depends(check_user)],
        file: UploadFile = File(...)):
    if not user:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    filename = f"{user.username}/avatar_{user.id}.png"
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        with Image.open(file.file) as img:
            img = img.convert("RGBA")
            img = center_crop(img)
            img = img.resize((512, 512))
            img.save(tmp_path, format="PNG")
        with open(tmp_path, "rb") as f:
            bucket.remove(paths=[filename])
            bucket.upload(
                path=filename, file=f, file_options={
                    "content-type": "image/png"})
        public_url = bucket.get_public_url(filename)
        adapter.update_by_id(User, user.id, {"avatar_url": public_url})
        return JSONResponse(
            {"message": "Profile picture updated", "url": public_url}, status_code=200
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.delete("/profile-picture", status_code=204)
async def del_pfp(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    if not user.avatar_url:
        return JSONResponse(
            {"message": "You don't have any avatars"}, status_code=404
        )
    filename = f"{user.username}/avatar_{user.id}.png"
    bucket.remove(paths=[filename])
    adapter.update_by_id(User, user.id, {"avatar_url": None})
    return JSONResponse(
        {"message": "Profile picture deleted"}, status_code=204)
