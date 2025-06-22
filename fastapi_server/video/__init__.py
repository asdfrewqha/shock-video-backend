from fastapi import APIRouter
from fastapi_server.video.upload_video import router as upd_router
from fastapi_server.video.get_video import router as get_router

router = APIRouter()

router.include_router(upd_router)
router.include_router(get_router)
