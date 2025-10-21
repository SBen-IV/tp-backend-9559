import uuid

from sqlmodel import Field, SQLModel


class ProblemaIncidenteLink(SQLModel, table=True):
    __tablename__: str = "problema_incidente_link"

    id_problema: uuid.UUID = Field(
        default=None, foreign_key="problemas.id", primary_key=True
    )
    id_incidente: uuid.UUID = Field(
        default=None, foreign_key="incidentes.id", primary_key=True
    )
