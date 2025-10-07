import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.incidents import IncidentesService as crud
from app.models.commons import Prioridad
from app.models.incidents import (
    CategoriaIncidente,
    EstadoIncidente,
    IncidenteCrear,
    IncidenteFilter,
    IncidentePublicoConItems,
)

router = APIRouter(prefix="/incidents")


@router.post("/", response_model=IncidentePublicoConItems)
async def create_incidente(
    session: SessionDep, current_user: CurrentUser, incidente_in: IncidenteCrear
) -> IncidentePublicoConItems:
    incidente_crear = IncidenteCrear.model_validate(
        incidente_in, update={"owner_id": current_user.id}
    )

    incidente = crud.create_incidente(session=session, incidente_crear=incidente_crear)

    return incidente


@router.get("/", response_model=list[IncidentePublicoConItems])
async def get_changes(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    categoria: CategoriaIncidente | None = None,
    estado: EstadoIncidente | None = None,
) -> list[IncidentePublicoConItems]:
    incidente_filter = IncidenteFilter(
        titulo=titulo,
        estado=estado,
        prioridad=prioridad,
        categoria=categoria,
    )
    return crud.get_incidentes(session=session, incidente_filter=incidente_filter)


@router.get("/{id_change}", response_model=IncidentePublicoConItems)
async def get_change(
    session: SessionDep, id_change: uuid.UUID
) -> IncidentePublicoConItems:
    return crud.get_incidente_by_id(session=session, id_change=id_change)
