import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from typing import TYPE_CHECKING, List

from sqlmodel import Field, SQLModel, Relationship

from .changes_items_link import CambioItemLink

if TYPE_CHECKING:
    from .changes import Cambio, CambioPublico
    

class CategoriaItem(str, Enum):
    SOFTWARE = "SOFTWARE"
    HARDWARE = "HARDWARE"
    DOCUMENTACION = "DOCUMENTACION"


class EstadoItem(str, Enum):
    PLANEADO = "PLANEADO"
    ENCARGADO = "ENCARGADO"
    EN_CREACION = "EN_CREACION"
    EN_PRUEBA = "EN_PRUEBA"
    EN_ALMACEN = "EN_ALMACEN"
    EN_PRODUCCION = "EN_PRODUCCION"
    EN_MANTENIMIENTO = "EN_MANTENIMIENTO"


class ItemConfiguracionBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    version: str = Field(min_length=1)
    categoria: CategoriaItem
    owner_id: None | uuid.UUID = Field(foreign_key="usuarios.id")
    estado: EstadoItem = Field(default=EstadoItem.PLANEADO)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    


class ItemConfiguracionCrear(SQLModel):
    nombre: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    version: str = Field(min_length=1)
    categoria: CategoriaItem
    owner_id: None | uuid.UUID = Field(default=None)
        

class ItemConfiguracionPublico(ItemConfiguracionBase):
    id: uuid.UUID
    
    cambios: List["CambioPublico"]
    

class ItemConfiguracion(ItemConfiguracionBase, table=True):
    __tablename__: str = "items_configuracion"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    
    cambios: None | List["Cambio"] = Relationship(back_populates="config_items", link_model=CambioItemLink)


@dataclass
class ItemConfiguracionFilter:
    nombre: str | None = None
    version: str | None = None
    categoria: CategoriaItem | None = None
    estado: EstadoItem | None = None
