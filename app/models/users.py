import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UsuarioBase(SQLModel):
    nombre: str = Field(max_length=255)
    apellido: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, max_length=255)


class UsuarioRegistrar(UsuarioBase):
    contraseña: str = Field(min_length=8, max_length=40)


class UsuarioPublico(UsuarioBase):
    id: uuid.UUID


class Usuario(UsuarioBase, table=True):
    __tablename__: str = "usuarios"
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    contraseña_hasheada: str
