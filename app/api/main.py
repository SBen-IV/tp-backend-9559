from fastapi import APIRouter

from app.api.routes import changes, login, users, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(changes.router, tags=["changes"])
api_router.include_router(utils.router, tags=["utils"])
