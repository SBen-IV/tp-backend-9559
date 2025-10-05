from fastapi import APIRouter

from app.api.routes import (
    changes,
    config_items,
    incidents,
    login,
    problems,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(config_items.router, tags=["config-items"])
api_router.include_router(changes.router, tags=["changes"])
api_router.include_router(problems.router, tags=["problems"])
api_router.include_router(incidents.router, tags=["incidents"])
api_router.include_router(utils.router, tags=["utils"])
