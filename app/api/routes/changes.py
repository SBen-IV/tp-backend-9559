from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models.changes import CambioCrear, CambioPublico

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublico)
async def create_change(
    session: SessionDep, cambio_crear: CambioCrear
) -> CambioPublico:
    return CambioPublico(
        titulo=cambio_crear.titulo,
        descripcion=cambio_crear.descripcion,
        prioridad=cambio_crear.prioridad,
    )
