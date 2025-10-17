import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud.incidents import IncidentesService as crud
from app.models.commons import Prioridad
from app.models.incidents import (
    CategoriaIncidente,
    EstadoIncidente,
    IncidenteActualizar,
    IncidenteCrear,
    IncidenteFilter,
    IncidentePublicoConItems,
)
from app.models.users import Rol

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
async def get_incidentes(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    categoria: CategoriaIncidente | None = None,
    estado: EstadoIncidente | None = None,
) -> list[IncidentePublicoConItems]:
    incidente_filter = IncidenteFilter(
        titulo=titulo,
        prioridad=prioridad,
        categoria=categoria,
        estado=estado,
    )
    return crud.get_incidentes(session=session, incidente_filter=incidente_filter)


@router.get("/{id_incidente}", response_model=IncidentePublicoConItems)
async def get_incidente(
    session: SessionDep, id_incidente: uuid.UUID
) -> IncidentePublicoConItems:
    return crud.get_incidente_by_id(session=session, id_incidente=id_incidente)


@router.patch("/{id_incidente}", response_model=IncidentePublicoConItems)
async def update_incidente(
    session: SessionDep,
    current_user: CurrentUser,
    id_incidente: uuid.UUID,
    incidente_actualizar: IncidenteActualizar,
) -> IncidentePublicoConItems:
    return crud.update_incidente(
        session=session,
        id_incidente=id_incidente,
        incidente_actualizar=incidente_actualizar,
    )


@router.delete("/{id_incidente}", response_model=IncidentePublicoConItems)
async def delete_incidente(
    session: SessionDep, current_user: CurrentUser, id_incidente: uuid.UUID
) -> IncidentePublicoConItems:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401, detail="Sólo empleados pueden eliminar un incidente"
        )

    return crud.delete_incidente(session=session, id_incidente=id_incidente)
