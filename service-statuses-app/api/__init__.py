from fastapi import APIRouter

from api.v1 import router as router_v1
from core.config import settings


router = APIRouter(prefix=settings.api_prefix)
router.include_router(router_v1)
