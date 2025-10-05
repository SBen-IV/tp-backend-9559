from sqlmodel import Session, select

from app.models.config_items import ItemConfiguracion
from app.models.problems import Problema, ProblemaCrear


class ProblemasService:
    def create_problema(*, session: Session, problema_crear: ProblemaCrear) -> Problema:
        db_obj = Problema.model_validate(problema_crear)

        config_items = session.exec(
            select(ItemConfiguracion).where(
                ItemConfiguracion.id.in_(problema_crear.id_config_items)
            )
        ).all()

        db_obj.config_items = config_items

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj
