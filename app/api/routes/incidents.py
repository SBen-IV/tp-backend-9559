import uuid

from app.crud.audits import AuditoriaService
from app.models.auditoria import AuditoriaCrear
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.deps import CurrentUser, SessionDep
from app.crud.incidents import IncidentesService as crud
from app.models.commons import Operacion, Prioridad, TipoEntidad
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

    incidente = crud.create_incidente(session=session, incidente_crear=incidente_crear, current_user_id=current_user.id)

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
    
    incidente =  crud.update_incidente(
        session=session,
        id_incidente=id_incidente,
        incidente_actualizar=incidente_actualizar,
    )
        
    auditoria_crear = AuditoriaCrear( 
        tipo_entidad = TipoEntidad.INCIDENTE,
        id_entidad = incidente.id,
        operacion = Operacion.ACTUALIZAR,
        estado_nuevo = jsonable_encoder(incidente),
        actualizado_por = current_user.id
    )
    AuditoriaService.registrar_operacion(session=session, auditoria_crear=auditoria_crear)
    
    return incidente


@router.delete("/{id_incidente}", response_model=IncidentePublicoConItems)
async def delete_incidente(
    session: SessionDep, current_user: CurrentUser, id_incidente: uuid.UUID
) -> IncidentePublicoConItems:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401, detail="Sólo empleados pueden eliminar un incidente"
        )

    incident =  crud.delete_incidente(session=session, id_incidente=id_incidente)
    
    auditoria_crear = AuditoriaCrear( 
        tipo_entidad = TipoEntidad.INCIDENTE,
        id_entidad = incident.id,
        operacion = Operacion.ELIMINAR,
        estado_nuevo = jsonable_encoder(incident),
        actualizado_por = current_user.id
    )
    AuditoriaService.registrar_operacion(session=session, auditoria_crear=auditoria_crear)    

    return incident