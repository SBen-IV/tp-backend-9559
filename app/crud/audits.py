import uuid
from http.client import HTTPException

from sqlmodel import Session, select

from app.models.auditoria import AuditoriaCrear, Auditoria, AuditoriaFilter

class AuditoriaService:
  def registrar_operacion(*, session: Session, auditoria_crear: AuditoriaCrear) -> Auditoria:
    auditoria_obj = Auditoria.model_validate(auditoria_crear)
    
    session.add(auditoria_obj)
    session.commit()
    session.refresh(auditoria_obj)
    
    return auditoria_obj
  
  def get_audits(*, session: Session, auditoria_filter: AuditoriaFilter) -> list[Auditoria]:
    query = select(Auditoria)

    if auditoria_filter.tipo_entidad is not None:
        query = query.where(Auditoria.tipo_entidad == auditoria_filter.tipo_entidad)

    if auditoria_filter.id_entidad is not None:
        query = query.where(Auditoria.id_entidad == auditoria_filter.id_entidad)

    if auditoria_filter.operacion is not None:
        query = query.where(Auditoria.operacion == auditoria_filter.operacion)
        
    query = query.order_by(Auditoria.fecha_actualizacion.desc())

    auditorias = session.exec(query).all()

    return auditorias
  
  def get_audit_by_id(*, session: Session, id_auditoria: uuid.UUID) -> Auditoria:
    auditoria = session.exec(select(Auditoria).where(Auditoria.id == id_auditoria)).first()

    if not auditoria:
        raise HTTPException(status_code=404, detail="No existe auditoría")

    return auditoria