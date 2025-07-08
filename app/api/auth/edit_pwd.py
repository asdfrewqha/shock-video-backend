import logging

import dns.resolver
from fastapi import APIRouter
from itsdangerous.url_safe import URLSafeTimedSerializer

from app.api.auth.tasks import send_confirmation_email_pwd
from app.core.celery_config import celery_app
from app.core.config import RANDOM_SECRET
from app.core.dependencies import badresponse, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User


router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/change-password-request")
async def change_pwd(email: str):
    user = await adapter.get_by_value(User, "email", email)
    if not user:
        return badresponse("User not found", 404)
    user = user[0]
    email_domain = email.split("@")[1]
    try:
        records = dns.resolver.resolve(email_domain, "MX")
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
    except Exception:
        return badresponse("Email is not valid", 403)
    serializer = URLSafeTimedSerializer(secret_key=RANDOM_SECRET)
    payld = serializer.dumps(str(user.id))
    logger.info(f"Celery broker URL: {celery_app.conf.broker_url}")
    send_confirmation_email_pwd.delay(email, payld)
    return okresp(200)
