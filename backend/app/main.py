import os

os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "1")

from fastapi import FastAPI

from app.api.routes import emails, health
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(emails.router, prefix="/api")
