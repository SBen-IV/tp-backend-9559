from sqlmodel import Field, SQLModel


class AppVersion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    version: str
