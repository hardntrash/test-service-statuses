from fastapi import APIRouter

from api.v1.services.routers import router as services_router


router = APIRouter(prefix='/v1')
router.include_router(services_router)
