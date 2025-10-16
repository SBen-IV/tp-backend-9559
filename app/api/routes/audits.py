import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.audits import AuditoriaService as crud
from app.models.auditoria import Auditoria, AuditoriaCrear
from app.crud.audits import AuditoriaService
from app.models.commons import TipoEntidad, Accion

router = APIRouter(prefix="/audits")


@router.get("", response_model=list[Auditoria])
async def get_audits(session: SessionDep) -> list[Auditoria]:
  return crud.get_audits(session=session)