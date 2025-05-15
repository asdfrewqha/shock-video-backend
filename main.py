from fastapi import FastAPI
from fastapi_server.auth import router as auth_router
from fastapi_server.user_info import router as user_info_router
import uvicorn
from config import FASTAPI_HOST, FASTAPI_PORT
from models.db_source.sqlite_adapter import adapter
app = FastAPI()


app.include_router(auth_router, tags=['Auth'])
app.include_router(user_info_router, tags=['User info'])




if __name__ == "__main__":
    adapter.initialize_tables()
    uvicorn.run(
        app=app, 
        host=FASTAPI_HOST, 
        port=int(FASTAPI_PORT)
    )
