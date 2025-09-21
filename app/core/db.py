import sqlalchemy as sa
from sqlmodel import Session, create_engine, select

from app.crud.users import UsuariosService
from app.db_seed import seed_usuarios
from app.models.app_version import AppVersion
from app.models.users import Usuario
from app.utils.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def set_version(session: Session, version: AppVersion) -> None:
    session.add(version)
    session.commit()


def populate_db(session: Session) -> None:
    usuarios = [usuario.email for usuario in session.exec(select(Usuario)).all()]

    for usuario in seed_usuarios:
        if usuario.email not in usuarios:
            UsuariosService.create_user(session=session, usuario_registrar=usuario)


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Check that the table exists in case its the first time running and there is no migration for AppVersion yet
    insp = sa.inspect(engine)

    if not insp.has_table("appversion"):
        return

    # Get version and update
    version = session.exec(select(AppVersion)).first()
    env_version = settings.APP_VERSION

    if not version:
        set_version(session, env_version)
    elif version.version < env_version.version:
        session.delete(version)
        set_version(session, env_version)

    populate_db(session)
