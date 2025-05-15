import os
from dotenv import load_dotenv


load_dotenv()


DB_URL = os.getenv('DB_URL')
FASTAPI_HOST = os.getenv('FASTAPI_HOST')
FASTAPI_PORT = os.getenv('FASTAPI_PORT')
RANDOM_SECRET = os.getenv('RANDOM_SECRET')