import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class EstadoCambio(str, Enum):
    RECIBIDO = "RECIBIDO"
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"
    EN_PROGRESO = "EN_PROGRESO"
    CERRADO = "CERRADO"


class CambioBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    prioridad: Prioridad
    estado: EstadoCambio = Field(default=EstadoCambio.RECIBIDO)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: None | uuid.UUID = Field(foreign_key="usuarios.id")


class CambioCrear(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    prioridad: Prioridad
    owner_id: None | uuid.UUID = Field(default=None)


class CambioPublico(CambioBase):
    id: uuid.UUID


class Cambio(CambioBase, table=True):
    __tablename__: str = "cambios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
