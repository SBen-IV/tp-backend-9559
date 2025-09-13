from sqlmodel import create_engine

from app.utils.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
