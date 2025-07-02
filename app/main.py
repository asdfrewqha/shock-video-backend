from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from app.core.config import FASTAPI_HOST, FASTAPI_PORT
from app.core.router_loader import include_all_routers
from app.models.db_source.db_adapter import adapter


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await adapter.initialize_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shock Video FastAPI", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan
    )

    include_all_routers(app)
    return app


app = create_app()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=FASTAPI_HOST, port=int(FASTAPI_PORT), reload=False)
