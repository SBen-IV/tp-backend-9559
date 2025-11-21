import uuid
from sqlmodel import Field, SQLModel

class CambioProblemaLink(SQLModel, table=True):
    __tablename__: str = "cambio_problema_link"
    
    id_cambio: uuid.UUID = Field(default=None, foreign_key="cambios.id", primary_key=True)
    id_problema: uuid.UUID = Field(default=None, foreign_key="problemas.id", primary_key=True)