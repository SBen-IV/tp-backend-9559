from fastapi import APIRouter

from app.api.routes import users, utils

api_router = APIRouter()
api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(users.router, tags=["users"])
