from fastapi import APIRouter

from fastapi_server.video.delete_video import router as del_router
from fastapi_server.video.get_video import router as get_router
from fastapi_server.video.get_video_by_id import router as gid_router
from fastapi_server.video.get_videos_by_user_id import router as gvi_router
from fastapi_server.video.like_video import router as lik_router
from fastapi_server.video.upload_video import router as upd_router
from fastapi_server.video.view_video import router as vew_router


router = APIRouter()

router.include_router(upd_router)
router.include_router(get_router)
router.include_router(gid_router)
router.include_router(del_router)
router.include_router(lik_router)
router.include_router(vew_router)
router.include_router(gvi_router)
