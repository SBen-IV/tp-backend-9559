import uuid

from app.crud.audits import AuditoriaService
from app.models.auditoria import AuditoriaCrear
from app.models.commons import Operacion, TipoEntidad
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
        *, session: Session, item_config_crear: ItemConfiguracionCrear, current_user_id: uuid
    ) -> ItemConfiguracion:
        db_obj = ItemConfiguracion.model_validate(item_config_crear)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        

        estado_nuevo = db_obj.model_dump(mode='json')
        auditoria_crear = AuditoriaCrear(
            tipo_entidad=TipoEntidad.CONFIG_ITEM,
            id_entidad=db_obj.id,
            operacion=Operacion.CREAR,
            estado_nuevo=estado_nuevo,
            actualizado_por=current_user_id,
        )
        AuditoriaService.registrar_operacion(
            session=session, auditoria_crear=auditoria_crear
        )

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

        if item_config_actualizar.categoria is not None:
            item_config.categoria = item_config_actualizar.categoria

        if item_config_actualizar.estado is not None:
            item_config.estado = item_config_actualizar.estado

        session.add(item_config)
        session.commit()
        session.refresh(item_config)

        return item_config

    def delete_item_configuracion(
        *, session: Session, id_item_config: uuid.UUID
    ) -> ItemConfiguracionPublico:
        item_config = ItemsConfiguracionService.get_item_configuracion_by_id(
            session=session, id_item_config=id_item_config
        )

        session.delete(item_config)
        session.commit()

        return item_config


    def rollback_item_config(
        *, session: Session, id_item_config: uuid.UUID, id_audit: uuid.UUID,current_user_id: uuid.UUID
    ) -> ItemConfiguracionPublico:
        item_actual = ItemsConfiguracionService.get_item_configuracion_by_id(session=session, id_item_config=id_item_config)
        
        auditoria = AuditoriaService.get_audit_by_id(session=session, id_auditoria=id_audit)
        
        if (auditoria.tipo_entidad != TipoEntidad.CONFIG_ITEM or auditoria.id_entidad != id_item_config):
            raise HTTPException(
                status_code=400, 
                detail="Auditoría no corresponde al ítem de configuración"
            )

        estado_anterior = auditoria.estado_nuevo
        
        item_actual.nombre = estado_anterior["nombre"]
        item_actual.descripcion = estado_anterior["descripcion"]
        item_actual.version = estado_anterior["version"]
        item_actual.categoria = estado_anterior["categoria"]
        item_actual.estado = estado_anterior["estado"]
        
        session.add(item_actual)
        session.commit()
        session.refresh(item_actual)
        
        return item_actual