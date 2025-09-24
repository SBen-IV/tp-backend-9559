import uuid
from enum import Enum

from sqlmodel import Field, SQLModel


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class CambioBase(SQLModel):
    titulo: str
    descripcion: str
    prioridad: Prioridad


class CambioCrear(CambioBase):
    pass


class CambioPublico(CambioBase):
    pass


class Cambio(CambioBase, table=True):
    __tablename__: str = "cambios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
