from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import router as api_router
from core.config import settings
from core.db import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_manager.dispose()


application = FastAPI(
    debug=settings.debug,
    title=settings.app_tittle,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

application.include_router(api_router)
