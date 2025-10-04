from datetime import datetime, timezone

from sqlmodel import Session, select

from app.crud.config_items import ItemsConfiguracionService as crud
from app.models.config_items import (
    CategoriaItem,
    EstadoItem,
    ItemConfiguracion,
    ItemConfiguracionCrear,
    ItemConfiguracionFilter,
)
from app.models.users import Usuario
from app.models.changes import Cambio, CambioPublico


def test_get_item_configuracion_by_nombre(session: Session) -> None:
    item_config_filter = ItemConfiguracionFilter(nombre="TV")
    items_config = crud.get_items_configuracion(
        session=session, item_config_filter=item_config_filter
    )

    assert len(items_config) == 1

    for item_config in items_config:
        assert item_config.nombre.lower().find(item_config_filter.nombre)


def test_create_item_configuracion(session: Session) -> None:
    now = datetime.now(timezone.utc)
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    item_config = ItemConfiguracionCrear(
        nombre="Windows 10",
        descripcion="Sistema Operativo",
        version="25H1",
        categoria=CategoriaItem.SOFTWARE,
        owner_id=usuario.id,
    )

    item_config_created = crud.create_item_configuracion(
        session=session, item_config_crear=item_config
    )

    assert item_config_created
    assert item_config_created.nombre == item_config.nombre
    assert item_config_created.descripcion == item_config.descripcion
    assert item_config_created.categoria == item_config.categoria

    item_config_db = session.exec(
        select(ItemConfiguracion).where(ItemConfiguracion.id == item_config_created.id)
    ).first()

    assert item_config_db
    assert item_config_db.nombre == item_config.nombre
    assert item_config_db.descripcion == item_config.descripcion
    assert item_config_db.categoria == item_config.categoria
    assert item_config_db.estado == EstadoItem.PLANEADO
    assert item_config_db.owner_id == usuario.id
    assert item_config_db.fecha_creacion.astimezone(timezone.utc) > now
