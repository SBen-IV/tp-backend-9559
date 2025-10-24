from datetime import datetime, timezone
import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.changes import (
    Cambio,
    CambioActualizar,
    CambioCrear,
    CambioFilter,
    CambioPublicoConItems,
    EstadoCambio,
)
from app.models.config_items import ItemConfiguracion


class CambiosService:
    def create_cambio(*, session: Session, cambio_crear: CambioCrear) -> Cambio:
        db_obj = Cambio.model_validate(cambio_crear)

        config_items = session.exec(
            select(ItemConfiguracion).where(
                ItemConfiguracion.id.in_(cambio_crear.id_config_items)
            )
        ).all()

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
            query = query.where(Cambio.titulo.ilike(f"%{cambio_filter.titulo}%"))

        if cambio_filter.descripcion is not None:
            query = query.where(
                Cambio.descripcion.ilike(f"%{cambio_filter.descripcion}%")
            )

        if cambio_filter.prioridad is not None:
            query = query.where(Cambio.prioridad == cambio_filter.prioridad)

        if cambio_filter.estado is not None:
            query = query.where(Cambio.estado == cambio_filter.estado)

        cambios = session.exec(query).all()

        return cambios

    def get_change_by_id(
        *, session: Session, id_change: uuid.UUID
    ) -> CambioPublicoConItems:
        cambio = session.exec(select(Cambio).where(Cambio.id == id_change)).first()

        if not cambio:
            raise HTTPException(status_code=404, detail="No existe cambio")

        return cambio

    def update_change(
        *, session: Session, id_change: uuid.UUID, cambio_actualizar: CambioActualizar
    ) -> CambioPublicoConItems:
        cambio = CambiosService.get_change_by_id(session=session, id_change=id_change)

        if cambio_actualizar.titulo is not None:
            cambio.titulo = cambio_actualizar.titulo

        if cambio_actualizar.descripcion is not None:
            cambio.descripcion = cambio_actualizar.descripcion

        if cambio_actualizar.prioridad is not None:
            cambio.prioridad = cambio_actualizar.prioridad

        if cambio_actualizar.estado is not None:
            cambio.estado = cambio_actualizar.estado
            if cambio_actualizar.estado == EstadoCambio.CERRADO.value:
                    cambio.fecha_cierre = datetime.now(timezone.utc)
            
        if cambio_actualizar.id_config_items is not None:
            config_items = session.exec(
                select(ItemConfiguracion).where(
                    ItemConfiguracion.id.in_(cambio_actualizar.id_config_items)
                )
            ).all()

            cambio.config_items = config_items

        session.add(cambio)
        session.commit()
        session.refresh(cambio)

        return cambio

    def delete_change(
        *, session: Session, id_change: uuid.UUID
    ) -> CambioPublicoConItems:
        cambio = CambiosService.get_change_by_id(session=session, id_change=id_change)

        session.delete(cambio)
        session.commit()

        return cambio
