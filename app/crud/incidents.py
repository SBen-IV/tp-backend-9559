import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.config_items import ItemConfiguracion
from app.models.incidents import (
    Incidente,
    IncidenteCrear,
    IncidenteFilter,
    IncidentePublicoConItems,
)


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

    def get_incidentes(
        *, session: Session, incidente_filter: IncidenteFilter
    ) -> list[IncidentePublicoConItems]:
        query = select(Incidente)

        if incidente_filter.titulo is not None:
            query = query.where(Incidente.titulo.ilike(f"%{incidente_filter.titulo}%"))

        if incidente_filter.prioridad is not None:
            query = query.where(Incidente.prioridad == incidente_filter.prioridad)

        if incidente_filter.categoria is not None:
            query = query.where(Incidente.categoria == incidente_filter.categoria)

        if incidente_filter.estado is not None:
            query = query.where(Incidente.estado == incidente_filter.estado)

        incidentes = session.exec(query).all()

        return incidentes

    def get_incidente_by_id(*, session: Session, id_incidente: uuid.UUID) -> Incidente:
        incidente = session.exec(
            select(Incidente).where(Incidente.id == id_incidente)
        ).first()

        if not incidente:
            raise HTTPException(status_code=404, detail="No existe incidente")

        return incidente
