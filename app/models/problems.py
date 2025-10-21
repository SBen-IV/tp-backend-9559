import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.commons import Prioridad
from app.models.problems_incidents_link import ProblemaIncidenteLink
from app.models.problems_items_link import ProblemaItemLink

if TYPE_CHECKING:
    from .config_items import ItemConfiguracion, ItemConfiguracionPublico
    from .incidents import Incidente, IncidentePublico


class EstadoProblema(str, Enum):
    EN_ANALISIS = "EN_ANALISIS"
    DETECTADO = "DETECTADO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"


class ProblemaBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: None | uuid.UUID = Field(foreign_key="usuarios.id")
    estado: EstadoProblema = Field(default=EstadoProblema.EN_ANALISIS)
    prioridad: Prioridad
    responsable_id: None | uuid.UUID = Field(default=None, foreign_key="usuarios.id")


class ProblemaCrear(SQLModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    owner_id: uuid.UUID | None = Field(default=None)
    prioridad: Prioridad
    id_config_items: list[uuid.UUID]
    id_incidentes: list[uuid.UUID]


class ProblemaPublico(ProblemaBase):
    id: uuid.UUID


class ProblemaPublicoConItems(ProblemaPublico):
    config_items: list["ItemConfiguracionPublico"] = []


class ProblemaPublicoConIncidentes(ProblemaPublicoConItems):
    incidentes: list["IncidentePublico"] = []


class Problema(ProblemaBase, table=True):
    __tablename__: str = "problemas"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    config_items: list["ItemConfiguracion"] = Relationship(
        back_populates="problemas", link_model=ProblemaItemLink
    )
    incidentes: list["Incidente"] = Relationship(
        back_populates="problemas", link_model=ProblemaIncidenteLink
    )


class ProblemaActualizar(SQLModel):
    titulo: str | None = Field(None, min_length=1)
    descripcion: str | None = Field(None, min_length=1)
    prioridad: Prioridad | None = None
    estado: EstadoProblema | None = None
    responsable_id: None | uuid.UUID = Field(default=None, foreign_key="usuarios.id")


@dataclass
class ProblemaFilter:
    titulo: str | None = None
    prioridad: Prioridad | None = None
    estado: EstadoProblema | None = None
