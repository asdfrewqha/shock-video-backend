import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from supabase import AsyncClient, create_async_client

from app.core.config import DEFAULT_AVATAR_URL, SUPABASE_API, SUPABASE_URL
from app.core.dependencies import badresponse, check_user, okresp
from app.models.auth_schemas import UpdateProfile
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User, Video


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
supabase: AsyncClient | None = None


async def get_supabase_client() -> AsyncClient:
    global supabase
    if supabase is None:
        supabase = await create_async_client(SUPABASE_URL, SUPABASE_API)
    return supabase


async def move_folder_video(old_path: str, new_path: str):
    supabase = await get_supabase_client()
    bucket = "videos"
    try:
        files = await supabase.storage.from_(bucket).list(
            path=f"{old_path}/",
            options={"recursive": True},
        )
    except Exception as e:
        logger.error(f"Ошибка получения списка файлов: {e}")
        return

    for file in files:
        filename = file["name"]
        old_full_path = f"{old_path}/{filename}"
        new_full_path = f"{new_path}/{filename}"

        try:
            await supabase.storage.from_(bucket).copy(old_full_path, new_full_path)
            public_url = await supabase.storage.from_(bucket).get_public_url(new_full_path)

            await adapter.update_by_id(Video, Path(filename).stem, {"url": public_url})

            await supabase.storage.from_(bucket).remove([old_full_path])
            logger.info(f"Перемещён: {old_full_path}>{new_full_path}")

        except Exception as e:
            logger.warning(f"Ошибка при перемещении файла {filename}: {e}")


@router.put("/update-profile")
async def upd_profile(user: Annotated[User, Depends(check_user)], update: UpdateProfile):
    if not user:
        return badresponse("Unauthorized", 401)

    updated_data = {}
    uid = user.id

    if update.name:
        updated_data["name"] = update.name

    if update.username:
        update.username = f"@{update.username}"
        existing_username = await adapter.get_by_value(User, "username", update.username)
        if not existing_username:
            updated_data["username"] = update.username
            if user.avatar_url != DEFAULT_AVATAR_URL:
                supabase = await get_supabase_client()
                old_pfp = f"{user.username}/avatar_{uid}.png"
                new_pfp = f"{update.username}/avatar_{uid}.png"
                try:
                    await supabase.storage.from_("pfps").copy(old_pfp, new_pfp)
                    await supabase.storage.from_("pfps").remove([old_pfp])
                    public_url = await supabase.storage.from_("pfps").get_public_url(new_pfp)
                    await adapter.update_by_id(User, uid, {"avatar_url": public_url})
                except Exception as e:
                    logger.error(f"Ошибка при перемещении аватара: {e}")
            await move_folder_video(user.username, update.username)
        else:
            return badresponse("This username is already taken", 409)

    if update.description:
        updated_data["description"] = update.description

    if not updated_data:
        return badresponse("No fields provided")

    await adapter.update_by_id(User, uid, updated_data)
    return okresp(message="Profile updated successfully")
