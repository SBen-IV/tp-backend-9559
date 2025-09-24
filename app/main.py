from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

from app.api.main import api_router
from app.utils.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="9559-backend",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": err['loc'][1], "message": err['msg']} for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "details": errors},
    )
