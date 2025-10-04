import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship

from .changes_items_link import CambioItemLink

from typing import TYPE_CHECKING, List  

if TYPE_CHECKING:
    from .config_items import ItemConfiguracion, ItemConfiguracionPublico


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
        
    config_items: List[uuid.UUID] = Field(..., min_length=1)


class CambioPublico(CambioBase):
    id: uuid.UUID
    
    config_items: List["ItemConfiguracionPublico"]


class Cambio(CambioBase, table=True):
    __tablename__: str = "cambios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    
    config_items: None | List["ItemConfiguracion"] = Relationship(back_populates="cambios", link_model=CambioItemLink)

