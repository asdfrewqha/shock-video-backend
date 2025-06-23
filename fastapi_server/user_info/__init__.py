from fastapi import APIRouter
from fastapi_server.user_info.me import router as me_router
from fastapi_server.user_info.admin import router as admin_router


router = APIRouter()


router.include_router(me_router)
router.include_router(admin_router)
