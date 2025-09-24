from sqlmodel import Session

from app.models.changes import Cambio, CambioCrear


class CambiosService:
    def create_cambio(*, session: Session, cambio_crear: CambioCrear) -> Cambio:
        return cambio_crear
        # db_obj = Cambio.model_validate(cambio_crear)
        #
        # session.add(db_obj)
        # session.commit()
        # session.refresh(db_obj)
        #
        # return db_obj
