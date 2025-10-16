import uuid
from http.client import HTTPException

from sqlmodel import Session, select

from app.models.auditoria import AuditoriaCrear, Auditoria

class AuditoriaService:
  def registrar_operacion(*, session: Session, auditoria_crear: AuditoriaCrear) -> Auditoria:
    auditoria_obj = Auditoria.model_validate(auditoria_crear)
    
    session.add(auditoria_obj)
    session.commit()
    session.refresh(auditoria_obj)
    
    return auditoria_obj
  
  def get_audits(*, session: Session) -> list[Auditoria]:
    auditorias = session.exec(select(Auditoria)).all()
    
    return auditorias