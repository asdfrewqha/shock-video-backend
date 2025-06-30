from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from config import FASTAPI_HOST, FASTAPI_PORT
from fastapi_server.auth import router as auth_router
from fastapi_server.user_info import router as user_info_router
from fastapi_server.video import router as video_router
from models.db_source.db_adapter import adapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.initialize_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Auth"])
app.include_router(user_info_router, tags=["User info"])
app.include_router(video_router, tags=["Video"])


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=FASTAPI_HOST, port=int(FASTAPI_PORT), reload=False)
