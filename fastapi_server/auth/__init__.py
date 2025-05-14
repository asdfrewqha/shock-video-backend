from fastapi import APIRouter
from fastapi_server.auth.register import router as register_router


router = APIRouter()


router.include_router(register_router)