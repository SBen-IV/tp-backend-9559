import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from app.models.problems import Problema
from sqlmodel import Field, Relationship, SQLModel

from .changes_items_link import CambioItemLink
from .changes_incidents_link import CambioIncidenteLink
from .changes_problems_link import CambioProblemaLink
from .commons import Prioridad

if TYPE_CHECKING:
    from .config_items import ItemConfiguracion, ItemConfiguracionPublico
    from .incidents import Incidente, IncidentePublico
    from .problems import Problema, ProblemaPublico


class EstadoCambio(str, Enum):
    RECIBIDO = "RECIBIDO"
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"
    EN_PROGRESO = "EN_PROGRESO"
    CERRADO = "CERRADO"


class ImpactoCambio(str, Enum):
    MENOR = "MENOR"
    SIGNIFICATIVO = "SIGNIFICATIVO"
    MAYOR = "MAYOR"


class CambioBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    prioridad: Prioridad
    impacto: ImpactoCambio
    estado: EstadoCambio = Field(default=EstadoCambio.RECIBIDO)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: None | uuid.UUID = Field(foreign_key="usuarios.id")
    fecha_cierre: datetime | None = Field(default=None)


class CambioCrear(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    prioridad: Prioridad
    impacto: ImpactoCambio
    owner_id: None | uuid.UUID = Field(default=None)

    id_config_items: list[uuid.UUID]
    id_incidentes: list[uuid.UUID] = Field(default=[])
    id_problemas: list[uuid.UUID] = Field(default=[])


class CambioPublico(CambioBase):
    id: uuid.UUID


class CambioPublicoConItems(CambioPublico):
    config_items: list["ItemConfiguracionPublico"] = []
    
    
class CambioPublicoConIncidentes(CambioPublico):
    incidentes: list["IncidentePublico"] = []
    

class CambioPublicoConProblemas(CambioPublico):
    problemas: list["ProblemaPublico"] = []    
    
    
class CambioPublicoConRelaciones(CambioPublicoConIncidentes, CambioPublicoConItems, CambioPublicoConProblemas):
    pass


class Cambio(CambioBase, table=True):
    __tablename__: str = "cambios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    config_items: list["ItemConfiguracion"] = Relationship(
        back_populates="cambios", link_model=CambioItemLink
    )
    incidentes: list["Incidente"] = Relationship(
        back_populates="cambios", link_model=CambioIncidenteLink
    )
    problemas: list["Problema"] = Relationship(
        back_populates="cambios", link_model=CambioProblemaLink
    )


class CambioActualizar(SQLModel):
    titulo: str | None = Field(None, min_length=1)
    descripcion: str | None = Field(None, min_length=1)
    prioridad: Prioridad | None = None
    estado: EstadoCambio | None = None
    impacto: ImpactoCambio | None = None
    id_config_items: None | list[uuid.UUID] = Field(
        default=None, foreign_key="items_configuracion.id"
    )
    id_incidentes: None | list[uuid.UUID] = Field(
        default=None, foreign_key="incidentes.id"
    )
    id_problemas: None | list[uuid.UUID] = Field(
        default=None, foreign_key="problemas.id"
    )


@dataclass
class CambioFilter:
    titulo: str | None = None
    descripcion: str | None = None
    prioridad: Prioridad | None = None
    estado: EstadoCambio | None = None
