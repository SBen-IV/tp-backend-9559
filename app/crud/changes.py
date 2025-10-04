from sqlmodel import Session, select

from app.models.changes import Cambio, CambioCrear
from app.models.config_items import ItemConfiguracion


class CambiosService:
    def create_cambio(*, session: Session, cambio_crear: CambioCrear) -> Cambio:
        db_obj = Cambio.model_validate(cambio_crear)
        
        config_items = session.exec(select(ItemConfiguracion).where(ItemConfiguracion.id.in_(cambio_crear.id_config_items))).all()

        db_obj.config_items = config_items

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj
