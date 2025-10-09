import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.config_items import (
    ItemConfiguracion,
    ItemConfiguracionActualizar,
    ItemConfiguracionCrear,
    ItemConfiguracionFilter,
    ItemConfiguracionPublico,
)


class ItemsConfiguracionService:
    def create_item_configuracion(
        *, session: Session, item_config_crear: ItemConfiguracionCrear
    ) -> ItemConfiguracion:
        db_obj = ItemConfiguracion.model_validate(item_config_crear)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj

    def get_items_configuracion(
        *, session: Session, item_config_filter: ItemConfiguracionFilter
    ) -> list[ItemConfiguracion]:
        query = select(ItemConfiguracion)

        if item_config_filter.nombre is not None:
            query = query.where(
                ItemConfiguracion.nombre.ilike(f"%{item_config_filter.nombre}%")
            )

        if item_config_filter.version is not None:
            query = query.where(
                ItemConfiguracion.version.ilike(f"%{item_config_filter.version}%")
            )

        if item_config_filter.categoria is not None:
            query = query.where(
                ItemConfiguracion.categoria == item_config_filter.categoria
            )

        if item_config_filter.estado is not None:
            query = query.where(ItemConfiguracion.estado == item_config_filter.estado)

        items_config = session.exec(query).all()

        return items_config

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

    def update_item_configuracion(
        *,
        session: Session,
        id_item_config: uuid.UUID,
        item_config_actualizar: ItemConfiguracionActualizar,
    ) -> ItemConfiguracionPublico:
        item_config = ItemsConfiguracionService.get_item_configuracion_by_id(
            session=session, id_item_config=id_item_config
        )

        if item_config_actualizar.nombre is not None:
            item_config.nombre = item_config_actualizar.nombre

        if item_config_actualizar.descripcion is not None:
            item_config.descripcion = item_config_actualizar.descripcion

        # if item_config_actualizar.prioridad is not None:
        #     item_config.prioridad = item_config_actualizar.prioridad
        #
        # if item_config_actualizar.estado is not None:
        #     item_config.estado = item_config_actualizar.estado
        #
        session.add(item_config)
        session.commit()
        session.refresh(item_config)

        return item_config
