from fastapi import FastAPI
from fastapi_server.auth import router as auth_router
import uvicorn
import os
from models.db_source.sqlite_adapter import adapter
app = FastAPI()


app.include_router(auth_router, tags=['Auth'])




if __name__ == "__main__":
    adapter.initialize_tables()
    server_address = os.getenv("SERVER_ADDRESS", "localhost:8081")
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))
