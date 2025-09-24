from sqlmodel import Session

from app.crud.changes import CambiosService as crud
from app.models.changes import CambioCrear, Prioridad


def test_create_cambio(session: Session) -> None:
    cambio = CambioCrear(
        titulo="Upgrade CPU",
        descripcion="2 cores to 32 cores",
        prioridad=Prioridad.URGENTE,
    )

    cambio_created = crud.create_cambio(session=session, cambio_crear=cambio)

    assert cambio_created
    assert cambio_created.titulo == cambio.titulo
