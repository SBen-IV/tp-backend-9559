import uuid
from datetime import datetime, timezone
from .commons import TipoEntidad, Accion

from sqlmodel import Field, SQLModel, JSON

  
class AuditoriaCrear(SQLModel):
  tipo_entidad: TipoEntidad
  id_entidad: uuid.UUID
  operacion: Accion
  actualizado_por: uuid.UUID = Field(foreign_key="usuarios.id")
  estado_nuevo: dict = Field(sa_type=JSON, default=None)


class Auditoria(AuditoriaCrear, table=True):
    __tablename__: str = "auditoria"
    fecha_acutalizacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    