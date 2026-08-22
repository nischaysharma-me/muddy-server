"""Central API v1 Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import agents, health, tools

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(tools.router)
api_router.include_router(agents.router)
