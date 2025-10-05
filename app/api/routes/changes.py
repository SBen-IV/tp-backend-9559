import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.changes import CambiosService as crud
from app.models.changes import (
    CambioCrear,
    CambioFilter,
    CambioPublicoConItems,
    EstadoCambio,
    Prioridad,
)

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublicoConItems)
async def create_change(
    session: SessionDep, current_user: CurrentUser, cambio_in: CambioCrear
) -> CambioPublicoConItems:
    cambio_crear = CambioCrear.model_validate(
        cambio_in, update={"owner_id": current_user.id}
    )

    cambio = crud.create_cambio(session=session, cambio_crear=cambio_crear)

    return cambio


@router.get("/", response_model=list[CambioPublicoConItems])
async def get_changes(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    estado: EstadoCambio | None = None,
    descripcion: str | None = None,
) -> list[CambioPublicoConItems]:
    cambio_filter = CambioFilter(
        titulo=titulo, estado=estado, prioridad=prioridad, descripcion=descripcion
    )
    return crud.get_changes(session=session, cambio_filter=cambio_filter)


@router.get("/{id_change}", response_model=CambioPublicoConItems)
async def get_change(
    session: SessionDep, id_change: uuid.UUID
) -> CambioPublicoConItems:
    return crud.get_change_by_id(session=session, id_change=id_change)
