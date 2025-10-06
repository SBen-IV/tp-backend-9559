from sqlmodel import Session, select

from app.models.config_items import ItemConfiguracion
from app.models.incidents import Incidente, IncidenteCrear


class IncidentesService:
    def create_incidente(
        *, session: Session, incidente_crear: IncidenteCrear
    ) -> Incidente:
        db_obj = Incidente.model_validate(incidente_crear)

        config_items = session.exec(
            select(ItemConfiguracion).where(
                ItemConfiguracion.id.in_(incidente_crear.id_config_items)
            )
        ).all()

        db_obj.config_items = config_items

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj
