from fastapi import APIRouter
from fastapi_server.auth.register import router as register_router
from fastapi_server.auth.token import router as token_router
from fastapi_server.auth.me import router as me_router
from fastapi_server.auth.admin import router as admin_router
from fastapi_server.auth.refresh import router as refresh_router


router = APIRouter()


router.include_router(register_router)
router.include_router(token_router)
router.include_router(me_router)
router.include_router(admin_router)
router.include_router(refresh_router)
