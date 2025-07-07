from celery import Celery

from app.core.config import REDIS_URL


print("Redis URL:", REDIS_URL)

celery_app = Celery(main="app", broker=REDIS_URL, backend=REDIS_URL)

celery_app.autodiscover_tasks(packages=["app.api.auth"])
