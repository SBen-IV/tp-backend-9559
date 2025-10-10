import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .changes_items_link import CambioItemLink
from .commons import Prioridad

if TYPE_CHECKING:
    from .config_items import ItemConfiguracion, ItemConfiguracionPublico


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

    id_config_items: list[uuid.UUID]


class CambioPublico(CambioBase):
    id: uuid.UUID


class CambioPublicoConItems(CambioPublico):
    config_items: list["ItemConfiguracionPublico"] = []


class Cambio(CambioBase, table=True):
    __tablename__: str = "cambios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    config_items: list["ItemConfiguracion"] = Relationship(
        back_populates="cambios", link_model=CambioItemLink
    )


class CambioActualizar(SQLModel):
    titulo: str | None = Field(None, min_length=1)
    descripcion: str | None = Field(None, min_length=1)
    prioridad: Prioridad | None = None
    estado: EstadoCambio | None = None


@dataclass
class CambioFilter:
    titulo: str | None = None
    descripcion: str | None = None
    prioridad: Prioridad | None = None
    estado: EstadoCambio | None = None
