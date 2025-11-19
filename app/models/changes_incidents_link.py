import uuid
from sqlmodel import Field, SQLModel

class CambioIncidenteLink(SQLModel, table=True):
    __tablename__: str = "cambio_incidente_link"
    
    id_cambio: uuid.UUID = Field(default=None, foreign_key="cambios.id", primary_key=True)
    id_incidente: uuid.UUID = Field(default=None, foreign_key="incidentes.id", primary_key=True)