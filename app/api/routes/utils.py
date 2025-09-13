from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health-check")
async def health_check() -> bool:
    return JSONResponse({"status": "ok"})
