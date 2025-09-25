from datetime import datetime, timezone

from sqlmodel import Session, select

from app.crud.changes import CambiosService as crud
from app.models.changes import Cambio, CambioCrear, EstadoCambio, Prioridad
from app.models.users import Usuario


def test_create_cambio(session: Session) -> None:
    now = datetime.now(timezone.utc)
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    cambio = CambioCrear(
        titulo="Upgrade CPU",
        descripcion="2 cores to 32 cores",
        prioridad=Prioridad.URGENTE,
        owner_id=usuario.id,
    )

    cambio_created = crud.create_cambio(session=session, cambio_crear=cambio)

    assert cambio_created
    assert cambio_created.titulo == cambio.titulo
    assert cambio_created.descripcion == cambio.descripcion
    assert cambio_created.prioridad == cambio.prioridad

    cambio_db = session.exec(
        select(Cambio).where(Cambio.id == cambio_created.id)
    ).first()

    assert cambio_db
    assert cambio_db.titulo == cambio.titulo
    assert cambio_db.descripcion == cambio.descripcion
    assert cambio_db.prioridad == cambio.prioridad
    assert cambio_db.estado == EstadoCambio.RECIBIDO
    assert cambio_db.owner_id == usuario.id
    assert cambio_db.fecha_creacion.astimezone(timezone.utc) > now
