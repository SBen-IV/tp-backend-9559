import uuid

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.deps import CurrentUser, SessionDep
from app.crud.audits import AuditoriaService
from app.crud.changes import CambiosService as crud
from app.models.auditoria import Auditoria, AuditoriaCrear, AuditoriaFilter
from app.models.changes import (
    CambioActualizar,
    CambioCrear,
    CambioFilter,
    CambioPublicoConRelaciones,
    EstadoCambio,
    Prioridad,
)
from app.models.commons import Operacion, TipoEntidad
from app.models.users import Rol

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublicoConRelaciones)
async def create_change(
    session: SessionDep, current_user: CurrentUser, cambio_in: CambioCrear
) -> CambioPublicoConRelaciones:
    cambio_crear = CambioCrear.model_validate(
        cambio_in, update={"owner_id": current_user.id}
    )

    cambio = crud.create_cambio(
        session=session, cambio_crear=cambio_crear, current_user_id=current_user.id
    )

    return cambio


@router.get("/", response_model=list[CambioPublicoConRelaciones])
async def get_changes(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    estado: EstadoCambio | None = None,
    descripcion: str | None = None,
) -> list[CambioPublicoConRelaciones]:
    cambio_filter = CambioFilter(
        titulo=titulo, estado=estado, prioridad=prioridad, descripcion=descripcion
    )
    return crud.get_changes(session=session, cambio_filter=cambio_filter)


@router.get("/{id_change}", response_model=CambioPublicoConRelaciones)
async def get_change(
    session: SessionDep, id_change: uuid.UUID
) -> CambioPublicoConRelaciones:
    return crud.get_change_by_id(session=session, id_change=id_change)


@router.patch("/{id_change}", response_model=CambioPublicoConRelaciones)
async def update_change(
    session: SessionDep,
    current_user: CurrentUser,
    id_change: uuid.UUID,
    cambio_actualizar: CambioActualizar,
) -> CambioPublicoConRelaciones:
    cambio = crud.update_change(
        session=session, id_change=id_change, cambio_actualizar=cambio_actualizar
    )

    estado_nuevo = cambio.model_dump(mode="json")
    estado_nuevo["id_config_items"] = [str(item.id) for item in cambio.config_items]
    estado_nuevo["id_incidentes"] = [
        str(incidente.id) for incidente in cambio.incidentes
    ]
    estado_nuevo["id_problemas"] = [str(problema.id) for problema in cambio.problemas]
    auditoria_crear = AuditoriaCrear(
        tipo_entidad=TipoEntidad.CAMBIO,
        id_entidad=cambio.id,
        operacion=Operacion.ACTUALIZAR,
        estado_nuevo=estado_nuevo,
        actualizado_por=current_user.id,
    )
    AuditoriaService.registrar_operacion(
        session=session, auditoria_crear=auditoria_crear
    )

    return cambio


@router.delete("/{id_change}", response_model=CambioPublicoConRelaciones)
async def delete_change(
    session: SessionDep, current_user: CurrentUser, id_change: uuid.UUID
) -> CambioPublicoConRelaciones:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401, detail="Sólo empleados pueden eliminar un cambio"
        )

    cambio = crud.delete_change(session=session, id_change=id_change)

    auditoria_crear = AuditoriaCrear(
        tipo_entidad=TipoEntidad.CAMBIO,
        id_entidad=cambio.id,
        operacion=Operacion.ELIMINAR,
        estado_nuevo=jsonable_encoder(cambio),
        actualizado_por=current_user.id,
    )
    AuditoriaService.registrar_operacion(
        session=session, auditoria_crear=auditoria_crear
    )

    return cambio


@router.get("/{id_change}/history", response_model=list[Auditoria])
async def get_history(
    session: SessionDep, current_user: CurrentUser, id_change: uuid.UUID
) -> list[Auditoria]:
    auditoria_filter = AuditoriaFilter(
        tipo_entidad=TipoEntidad.CAMBIO, id_entidad=id_change
    )

    return AuditoriaService.get_audits(
        session=session, auditoria_filter=auditoria_filter
    )


@router.post("/{id_change}/rollback", response_model=CambioPublicoConRelaciones)
async def rollback_change(
    session: SessionDep,
    current_user: CurrentUser,
    id_change: uuid.UUID,
    id_auditoria: uuid.UUID,
) -> CambioPublicoConRelaciones:
    cambio = crud.get_change_by_id(session=session, id_change=id_change)

    cambio_rollback = crud.rollback_change(
        session=session,
        id_change=id_change,
        id_audit=id_auditoria,
        current_user_id=current_user.id,
    )

    return cambio_rollback
