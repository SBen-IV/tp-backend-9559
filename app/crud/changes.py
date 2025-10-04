from sqlmodel import Session, select

from app.models.changes import Cambio, CambioCrear, CambioFilter, CambioPublicoConItems
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

    def get_changes(
        *, session: Session, cambio_filter: CambioFilter
    ) -> list[CambioPublicoConItems]:
        query = select(Cambio)

        if cambio_filter.titulo is not None:
            query = query.where(
                Cambio.titulo.ilike(f"%{cambio_filter.titulo}%")
            )

        if cambio_filter.descripcion is not None:
            query = query.where(
                Cambio.descripcion.ilike(f"%{cambio_filter.descripcion}%")
            )

        if cambio_filter.prioridad is not None:
            query = query.where(
                Cambio.prioridad == cambio_filter.prioridad
            )

        if cambio_filter.estado is not None:
            query = query.where(Cambio.estado == cambio_filter.estado)

        items_config = session.exec(query).all()

        return items_config