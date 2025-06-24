from fastapi import APIRouter

from fastapi_server.user_info.admin import router as admin_router
from fastapi_server.user_info.get_likes import router as likes_router
from fastapi_server.user_info.get_user_by_id import router as gubi_router
from fastapi_server.user_info.me import router as me_router
from fastapi_server.user_info.upload_pfp import router as upd_pfp_router

router = APIRouter()


router.include_router(me_router)
router.include_router(admin_router)
router.include_router(upd_pfp_router)
router.include_router(gubi_router)
router.include_router(likes_router)
