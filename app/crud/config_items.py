from sqlmodel import Session

from app.models.config_items import ItemConfiguracion, ItemConfiguracionCrear


class ItemsConfiguracionService:
    def create_item_configuracion(
        *, session: Session, item_config_crear: ItemConfiguracionCrear
    ) -> ItemConfiguracion:
        db_obj = ItemConfiguracion.model_validate(item_config_crear)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj
