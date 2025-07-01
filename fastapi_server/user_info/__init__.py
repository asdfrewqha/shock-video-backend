from fastapi import APIRouter

from fastapi_server.user_info.admin import router as admin_router
from fastapi_server.user_info.get_user_by_id import router as gubi_router
from fastapi_server.user_info.load_pfp import router as load_pfp_router
from fastapi_server.user_info.profile import router as profile_router
from fastapi_server.user_info.upload_pfp import router as upd_pfp_router


router = APIRouter()


router.include_router(profile_router)
router.include_router(admin_router)
router.include_router(upd_pfp_router)
router.include_router(gubi_router)
router.include_router(load_pfp_router)
