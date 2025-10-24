import uuid

from app.models.commons import Operacion, TipoEntidad
from fastapi import APIRouter

from app.api.deps import SessionDep
from app.crud.audits import AuditoriaService as crud
from app.models.auditoria import Auditoria, AuditoriaFilter

router = APIRouter(prefix="/audits")


@router.get("", response_model=list[Auditoria])
async def get_audits(
    session: SessionDep,
    tipo_entidad: TipoEntidad | None = None,
    id_entidad: uuid.UUID | None = None,
    operacion: Operacion | None = None
) -> list[Auditoria]:
    auditoria_filter = AuditoriaFilter(
        tipo_entidad=tipo_entidad, id_entidad=id_entidad, operacion=operacion
    )
    return crud.get_audits(session=session, auditoria_filter=auditoria_filter)

@router.get("/{id_auditoria}", response_model=Auditoria)
async def get_audit_by_id(
    session: SessionDep,
    id_auditoria: uuid.UUID
) -> Auditoria:
    return crud.get_audit_by_id(session=session, id_auditoria=id_auditoria)