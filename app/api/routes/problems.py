import uuid

from app.crud.audits import AuditoriaService
from app.models.auditoria import AuditoriaCrear
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud.problems import ProblemasService as crud
from app.models.commons import Operacion, Prioridad, TipoEntidad
from app.models.problems import (
    EstadoProblema,
    ProblemaActualizar,
    ProblemaCrear,
    ProblemaFilter,
    ProblemaPublicoConItems,
)
from app.models.users import Rol

router = APIRouter(prefix="/problems")


@router.post("/", response_model=ProblemaPublicoConItems)
async def create_problema(
    session: SessionDep, current_user: CurrentUser, problema_in: ProblemaCrear
) -> ProblemaPublicoConItems:
    problema_crear = ProblemaCrear.model_validate(
        problema_in, update={"owner_id": current_user.id}
    )

    problema = crud.create_problema(session=session, problema_crear=problema_crear)
    
    auditoria_crear = AuditoriaCrear( 
        tipo_entidad = TipoEntidad.PROBLEMA,
        id_entidad = problema.id,
        operacion = Operacion.CREAR,
        estado_nuevo = jsonable_encoder(problema),
        actualizado_por = current_user.id
    )
    AuditoriaService.registrar_operacion(session=session, auditoria_crear=auditoria_crear)

    return problema


@router.get("/", response_model=list[ProblemaPublicoConItems])
async def get_problemas(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    estado: EstadoProblema | None = None,
) -> list[ProblemaPublicoConItems]:
    problema_filter = ProblemaFilter(
        titulo=titulo,
        prioridad=prioridad,
        estado=estado,
    )
    return crud.get_problemas(session=session, problema_filter=problema_filter)


@router.get("/{id_problema}", response_model=ProblemaPublicoConItems)
async def get_problema(
    session: SessionDep, id_problema: uuid.UUID
) -> ProblemaPublicoConItems:
    return crud.get_problema_by_id(session=session, id_problema=id_problema)


@router.patch("/{id_problema}", response_model=ProblemaPublicoConItems)
async def update_problema(
    session: SessionDep,
    current_user: CurrentUser,
    id_problema: uuid.UUID,
    problema_actualizar: ProblemaActualizar,
) -> ProblemaPublicoConItems:
    return crud.update_problema(
        session=session,
        id_problema=id_problema,
        problema_actualizar=problema_actualizar,
    )


@router.delete("/{id_problema}", response_model=ProblemaPublicoConItems)
async def delete_problema(
    session: SessionDep, current_user: CurrentUser, id_problema: uuid.UUID
) -> ProblemaPublicoConItems:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401, detail="Sólo empleados pueden eliminar un problema"
        )

    return crud.delete_problema(session=session, id_problema=id_problema)
