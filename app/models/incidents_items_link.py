import uuid

from sqlmodel import Field, SQLModel


class IncidenteItemLink(SQLModel, table=True):
    __tablename__: str = "incidente_item_link"

    id_incidente: uuid.UUID = Field(
        default=None, foreign_key="incidentes.id", primary_key=True
    )
    id_config_item: uuid.UUID = Field(
        default=None, foreign_key="items_configuracion.id", primary_key=True
    )
