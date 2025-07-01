import importlib
import logging
import pkgutil

from fastapi import FastAPI

from app import api


logger = logging.getLogger(__name__)


def include_all_routers(app: FastAPI):
    for _, module_name, _ in pkgutil.walk_packages(api.__path__, prefix="app.api."):
        module = importlib.import_module(module_name)

        if hasattr(module, "router"):
            parts = module_name.split(".")
            tag = parts[2] if len(parts) >= 3 else "default"

            app.include_router(module.router, tags=[tag])
            logger.info(f"Included router from: {module_name} (tag: {tag})")
