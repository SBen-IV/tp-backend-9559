import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

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

    def get_item_configuracion_by_id(
        *, session: Session, id_item_config: uuid.UUID
    ) -> ItemConfiguracion:
        item_config = session.exec(
            select(ItemConfiguracion).where(ItemConfiguracion.id == id_item_config)
        ).first()
        if not item_config:
            raise HTTPException(
                status_code=404, detail="No existe item de configuracion"
            )
        return item_config
