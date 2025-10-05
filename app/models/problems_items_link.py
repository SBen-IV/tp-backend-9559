import uuid

from sqlmodel import Field, SQLModel


class ProblemaItemLink(SQLModel, table=True):
    __tablename__: str = "problema_item_link"

    id_problema: uuid.UUID = Field(
        default=None, foreign_key="problemas.id", primary_key=True
    )
    id_config_item: uuid.UUID = Field(
        default=None, foreign_key="items_configuracion.id", primary_key=True
    )

