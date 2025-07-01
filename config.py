import logging
import os

from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_AVATAR_URL = "https://uozfhywwucahpeysjtvy.supabase.co/storage/v1/object/public/pfps/0/avatar_00000000-0000-0000-0000-000000000000.png"  # noqa

PGR_USER = os.getenv("PGR_USER")
USER = os.getenv("USER", PGR_USER)
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")
FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = os.getenv("FASTAPI_PORT")
RANDOM_SECRET = os.getenv("RANDOM_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API = os.getenv("SUPABASE_API")
UUID_SHA = os.getenv("UUID_SHA")

DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

logging.info(DATABASE_URL)
