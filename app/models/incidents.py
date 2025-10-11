import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .commons import Prioridad
from .incidents_items_link import IncidenteItemLink

if TYPE_CHECKING:
    from .config_items import ItemConfiguracion, ItemConfiguracionPublico


class EstadoIncidente(str, Enum):
    NUEVO = "NUEVO"
    EN_PROGRESO = "EN_PROGRESO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"


class CategoriaIncidente(str, Enum):
    SOFTWARE = "SOFTWARE"
    HARDWARE = "HARDWARE"
    SOLICITUD_DE_SERVICIO = "SOLICITUD_DE_SERVICIO"
    SEGURIDAD = "SEGURIDAD"


class IncidenteBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: None | uuid.UUID = Field(foreign_key="usuarios.id")
    estado: EstadoIncidente = Field(default=EstadoIncidente.NUEVO)
    prioridad: Prioridad
    categoria: CategoriaIncidente
    responsable_id: None | uuid.UUID = Field(default=None, foreign_key="usuarios.id")


class IncidenteCrear(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    owner_id: uuid.UUID | None = Field(default=None)
    prioridad: Prioridad
    categoria: CategoriaIncidente
    id_config_items: list[uuid.UUID]


class IncidentePublico(IncidenteBase):
    id: uuid.UUID


class IncidentePublicoConItems(IncidentePublico):
    config_items: list["ItemConfiguracionPublico"] = []


class Incidente(IncidenteBase, table=True):
    __tablename__: str = "incidentes"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    config_items: list["ItemConfiguracion"] = Relationship(
        back_populates="incidentes", link_model=IncidenteItemLink
    )

class IncidenteActualizar(SQLModel):
    titulo: str | None = Field(None, min_length=1)
    descripcion: str | None = Field(None, min_length=1)
    prioridad: Prioridad | None = None
    estado: EstadoIncidente | None = None
    categoria: CategoriaIncidente | None = None
    responsable_id: None | uuid.UUID = Field(default=None, foreign_key="usuarios.id")

@dataclass
class IncidenteFilter:
    titulo: str | None = None
    prioridad: Prioridad | None = None
    categoria: CategoriaIncidente | None = None
    estado: EstadoIncidente | None = None
