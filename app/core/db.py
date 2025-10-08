import sqlalchemy as sa
from sqlmodel import Session, create_engine, select

from app.crud.changes import CambiosService
from app.crud.config_items import ItemsConfiguracionService
from app.crud.incidents import IncidentesService
from app.crud.problems import ProblemasService
from app.crud.users import UsuariosService
from app.db_seed import (
    seed_cambios,
    seed_incidentes,
    seed_items_config,
    seed_problemas,
    seed_usuarios,
)
from app.models.app_version import AppVersion
from app.models.changes import Cambio
from app.models.config_items import ItemConfiguracion
from app.models.incidents import Incidente
from app.models.problems import Problema
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

    usuario = session.exec(select(Usuario)).first()

    # `nombre` is not unique but it's the only way to check for duplicates
    items_config = [
        item_config.nombre
        for item_config in session.exec(select(ItemConfiguracion)).all()
    ]

    for item_config in seed_items_config:
        if item_config.nombre not in items_config:
            item_config.owner_id = usuario.id
            ItemsConfiguracionService.create_item_configuracion(
                session=session, item_config_crear=item_config
            )

    id_items_config = [
        item_config.id for item_config in session.exec(select(ItemConfiguracion)).all()
    ]

    cambios = [cambio.titulo for cambio in session.exec(select(Cambio)).all()]

    for cambio in seed_cambios:
        if cambio.titulo not in cambios:
            cambio.owner_id = usuario.id
            cambio.id_config_items = [id_items_config[0]]
            CambiosService.create_cambio(session=session, cambio_crear=cambio)

    incidentes = [
        incidente.titulo for incidente in session.exec(select(Incidente)).all()
    ]

    for incidente in seed_incidentes:
        if incidente.titulo not in incidentes:
            incidente.owner_id = usuario.id
            incidente.id_config_items = [id_items_config[0]]
            IncidentesService.create_incidente(
                session=session, incidente_crear=incidente
            )

    problemas = [problema.titulo for problema in session.exec(select(Problema)).all()]

    for problema in seed_problemas:
        if problema.titulo not in problemas:
            problema.owner_id = usuario.id
            problema.id_config_items = [id_items_config[0]]
            ProblemasService.create_problema(session=session, problema_crear=problema)


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
