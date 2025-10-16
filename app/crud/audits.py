import uuid
from http.client import HTTPException

from app.api.deps import CurrentUser
from sqlmodel import Session, select

from app.models.auditoria import AuditoriaBase, Auditoria

class AuditoriaService:
  def registrar_accion(*, session: Session, current_user: CurrentUser, auditoria_crear: AuditoriaBase) -> Auditoria:
    auditoria_obj = AuditoriaBase.model_validate(auditoria_crear, update={"actualizado_por": current_user.id})
    
    session.add(auditoria_obj)
    session.commit()
    session.refresh(auditoria_obj)