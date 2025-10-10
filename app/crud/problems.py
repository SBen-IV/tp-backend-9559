import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.config_items import ItemConfiguracion
from app.models.problems import (
    Problema,
    ProblemaActualizar,
    ProblemaCrear,
    ProblemaFilter,
    ProblemaPublicoConItems,
)


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

    def get_problemas(
        *, session: Session, problema_filter: ProblemaFilter
    ) -> list[ProblemaPublicoConItems]:
        query = select(Problema)

        if problema_filter.titulo is not None:
            query = query.where(Problema.titulo.ilike(f"%{problema_filter.titulo}%"))

        if problema_filter.prioridad is not None:
            query = query.where(Problema.prioridad == problema_filter.prioridad)

        if problema_filter.estado is not None:
            query = query.where(Problema.estado == problema_filter.estado)

        problemas = session.exec(query).all()

        return problemas

    def get_problema_by_id(*, session: Session, id_problema: uuid.UUID) -> Problema:
        problema = session.exec(
            select(Problema).where(Problema.id == id_problema)
        ).first()

        if not problema:
            raise HTTPException(status_code=404, detail="No existe problema")

        return problema

    def update_problema(
        *, session: Session, id_problema: uuid.UUID, problema_actualizar: ProblemaActualizar
    ) -> ProblemaPublicoConItems:
        problema = ProblemasService.get_problema_by_id(session=session, id_problema=id_problema)

        if problema_actualizar.titulo is not None:
            problema.titulo = problema_actualizar.titulo

        session.add(problema)
        session.commit()
        session.refresh(problema)

        return problema