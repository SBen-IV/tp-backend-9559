from sqlmodel import SQLModel


class AppVersion(SQLModel):
    version: str
