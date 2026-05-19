from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.fragments import router as fragments_router
from app.api.routes.health import router as health_router
from app.api.routes.playback import router as playback_router
from app.api.routes.videos import router as videos_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(videos_router)
api_router.include_router(fragments_router)
api_router.include_router(playback_router)
