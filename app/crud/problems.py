import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.config_items import ItemConfiguracion
from app.models.incidents import Incidente
from app.models.problems import (
    EstadoProblema,
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

        incidentes = session.exec(
            select(Incidente).where(Incidente.id.in_(problema_crear.id_incidentes))
        ).all()

        db_obj.config_items = config_items
        db_obj.incidentes = incidentes

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
        *,
        session: Session,
        id_problema: uuid.UUID,
        problema_actualizar: ProblemaActualizar,
    ) -> ProblemaPublicoConItems:
        problema = ProblemasService.get_problema_by_id(
            session=session, id_problema=id_problema
        )

        if problema_actualizar.titulo is not None:
            problema.titulo = problema_actualizar.titulo

        if problema_actualizar.descripcion is not None:
            problema.descripcion = problema_actualizar.descripcion

        if problema_actualizar.estado is not None:
            problema.estado = problema_actualizar.estado

            if problema_actualizar.estado == EstadoProblema.CERRADO:
                problema.fecha_cierre = datetime.now(timezone.utc)

        if problema_actualizar.responsable_id is not None:
            problema.responsable_id = problema_actualizar.responsable_id

        if problema_actualizar.prioridad is not None:
            problema.prioridad = problema_actualizar.prioridad

        if problema_actualizar.solucion is not None:
            problema.solucion = problema_actualizar.solucion

        if problema_actualizar.id_incidentes is not None:
            incidentes = session.exec(
                select(Incidente).where(
                    Incidente.id.in_(problema_actualizar.id_incidentes)
                )
            ).all()

            problema.incidentes = incidentes

        if problema_actualizar.id_config_items is not None:
            config_items = session.exec(
                select(ItemConfiguracion).where(
                    ItemConfiguracion.id.in_(problema_actualizar.id_config_items)
                )
            ).all()

            problema.config_items = config_items

        session.add(problema)
        session.commit()
        session.refresh(problema)

        return problema

    def delete_problema(
        *, session: Session, id_problema: uuid.UUID
    ) -> ProblemaPublicoConItems:
        problema = ProblemasService.get_problema_by_id(
            session=session, id_problema=id_problema
        )

        session.delete(problema)
        session.commit()

        return problema
