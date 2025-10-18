import uuid

from app.crud.audits import AuditoriaService
from app.models.auditoria import AuditoriaCrear
from app.models.commons import Operacion, TipoEntidad
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.deps import CurrentUser, SessionDep
from app.crud.changes import CambiosService as crud
from app.models.changes import (
    CambioActualizar,
    CambioCrear,
    CambioFilter,
    CambioPublicoConItems,
    EstadoCambio,
    Prioridad,
)
from app.models.users import Rol

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublicoConItems)
async def create_change(
    session: SessionDep, current_user: CurrentUser, cambio_in: CambioCrear
) -> CambioPublicoConItems:
    cambio_crear = CambioCrear.model_validate(
        cambio_in, update={"owner_id": current_user.id}
    )

    cambio = crud.create_cambio(session=session, cambio_crear=cambio_crear)
    
    auditoria_crear = AuditoriaCrear( 
        tipo_entidad = TipoEntidad.CAMBIO,
        id_entidad = cambio.id,
        operacion = Operacion.CREAR,
        estado_nuevo = jsonable_encoder(cambio),
        actualizado_por = current_user.id
    )
    AuditoriaService.registrar_operacion(session=session, auditoria_crear=auditoria_crear)

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


@router.patch("/{id_change}", response_model=CambioPublicoConItems)
async def update_change(
    session: SessionDep,
    current_user: CurrentUser,
    id_change: uuid.UUID,
    cambio_actualizar: CambioActualizar,
) -> CambioPublicoConItems:
    return crud.update_change(
        session=session, id_change=id_change, cambio_actualizar=cambio_actualizar
    )


@router.delete("/{id_change}", response_model=CambioPublicoConItems)
async def delete_change(
    session: SessionDep, current_user: CurrentUser, id_change: uuid.UUID
) -> CambioPublicoConItems:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401, detail="Sólo empleados pueden eliminar un cambio"
        )

    return crud.delete_change(session=session, id_change=id_change)
