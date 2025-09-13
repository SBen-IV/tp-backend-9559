from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.deps import SessionDep
from app.crud.utils import AppVersionService as crud

router = APIRouter(prefix="/utils")


@router.get("/health-check")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "OK"})


@router.get("/version")
async def get_version(session: SessionDep) -> JSONResponse:
    version = crud.get_version(session=session)

    return JSONResponse({"version": version.version})
