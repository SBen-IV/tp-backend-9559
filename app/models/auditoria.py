from dataclasses import dataclass
import uuid
from datetime import datetime, timezone
from .commons import TipoEntidad, Operacion

from sqlmodel import Field, SQLModel, JSON

  
class AuditoriaCrear(SQLModel):
  tipo_entidad: TipoEntidad
  id_entidad: uuid.UUID
  operacion: Operacion
  actualizado_por: uuid.UUID = Field(foreign_key="usuarios.id")
  estado_nuevo: dict = Field(sa_type=JSON, default=None)


class Auditoria(AuditoriaCrear, table=True):
    __tablename__: str = "auditorias"
    fecha_actualizacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    
      
@dataclass
class AuditoriaFilter:
  tipo_entidad: TipoEntidad | None = None
  id_entidad: uuid.UUID | None = None
  operacion: Operacion | None = None
  