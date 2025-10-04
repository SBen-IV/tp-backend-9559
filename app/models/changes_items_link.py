import uuid
from sqlmodel import Field, SQLModel

class CambioItemLink(SQLModel, table=True):
    __tablename__: str = "cambio_item_link"
    
    id_cambio: uuid.UUID = Field(default=None, foreign_key="cambios.id", primary_key=True)
    id_config_item: uuid.UUID = Field(default=None, foreign_key="items_configuracion.id", primary_key=True)