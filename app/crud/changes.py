import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.crud.audits import AuditoriaService
from app.models.auditoria import AuditoriaCrear
from app.models.changes import (
    Cambio,
    CambioActualizar,
    CambioCrear,
    CambioFilter,
    CambioPublicoConRelaciones,
    EstadoCambio,
)
from app.models.commons import Operacion, TipoEntidad
from app.models.config_items import ItemConfiguracion
from app.models.incidents import Incidente
from app.models.problems import Problema


class CambiosService:
    def create_cambio(
        *, session: Session, cambio_crear: CambioCrear, current_user_id: uuid
    ) -> Cambio:
        db_obj = Cambio.model_validate(cambio_crear)

        config_items = session.exec(
            select(ItemConfiguracion).where(
                ItemConfiguracion.id.in_(cambio_crear.id_config_items)
            )
        ).all()
        incidentes = session.exec(
            select(Incidente).where(Incidente.id.in_(cambio_crear.id_incidentes))
        ).all()
        problemas = session.exec(
            select(Problema).where(Problema.id.in_(cambio_crear.id_problemas))
        ).all()

        db_obj.config_items = config_items
        db_obj.incidentes = incidentes
        db_obj.problemas = problemas

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        estado_nuevo = db_obj.model_dump(mode="json")
        estado_nuevo["id_config_items"] = [str(item.id) for item in db_obj.config_items]
        estado_nuevo["id_incidentes"] = [
            str(incidente.id) for incidente in db_obj.incidentes
        ]
        estado_nuevo["id_problemas"] = [
            str(problema.id) for problema in db_obj.problemas
        ]
        estado_nuevo["responsable_id"] = None

        auditoria_crear = AuditoriaCrear(
            tipo_entidad=TipoEntidad.CAMBIO,
            id_entidad=db_obj.id,
            operacion=Operacion.CREAR,
            estado_nuevo=estado_nuevo,
            actualizado_por=current_user_id,
        )
        AuditoriaService.registrar_operacion(
            session=session, auditoria_crear=auditoria_crear
        )

        return db_obj

    def get_changes(
        *, session: Session, cambio_filter: CambioFilter
    ) -> list[CambioPublicoConRelaciones]:
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
    ) -> CambioPublicoConRelaciones:
        cambio = session.exec(select(Cambio).where(Cambio.id == id_change)).first()

        if not cambio:
            raise HTTPException(status_code=404, detail="No existe cambio")

        return cambio

    def update_change(
        *, session: Session, id_change: uuid.UUID, cambio_actualizar: CambioActualizar
    ) -> CambioPublicoConRelaciones:
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

        if cambio_actualizar.impacto is not None:
            cambio.impacto = cambio_actualizar.impacto

        if cambio_actualizar.id_config_items is not None:
            config_items = session.exec(
                select(ItemConfiguracion).where(
                    ItemConfiguracion.id.in_(cambio_actualizar.id_config_items)
                )
            ).all()

            cambio.config_items = config_items

        if cambio_actualizar.id_incidentes is not None:
            incidentes = session.exec(
                select(Incidente).where(
                    Incidente.id.in_(cambio_actualizar.id_incidentes)
                )
            ).all()

            cambio.incidentes = incidentes

        if cambio_actualizar.id_problemas is not None:
            problemas = session.exec(
                select(Problema).where(Problema.id.in_(cambio_actualizar.id_problemas))
            ).all()

            cambio.problemas = problemas

        if cambio_actualizar.responsable_id is not None:
            cambio.responsable_id = cambio_actualizar.responsable_id

        session.add(cambio)
        session.commit()
        session.refresh(cambio)

        return cambio

    def delete_change(
        *, session: Session, id_change: uuid.UUID
    ) -> CambioPublicoConRelaciones:
        cambio = CambiosService.get_change_by_id(session=session, id_change=id_change)

        session.delete(cambio)
        session.commit()

        return cambio

    def rollback_change(
        *,
        session: Session,
        id_change: uuid.UUID,
        id_audit: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> CambioPublicoConRelaciones:
        cambio_actual = CambiosService.get_change_by_id(
            session=session, id_change=id_change
        )

        auditoria = AuditoriaService.get_audit_by_id(
            session=session, id_auditoria=id_audit
        )

        if (
            auditoria.tipo_entidad != TipoEntidad.CAMBIO
            or auditoria.id_entidad != id_change
        ):
            raise HTTPException(
                status_code=400, detail="Auditoría no corresponde al cambio"
            )

        estado_anterior = auditoria.estado_nuevo

        cambio_actual.titulo = estado_anterior["titulo"]
        cambio_actual.descripcion = estado_anterior["descripcion"]
        cambio_actual.prioridad = estado_anterior["prioridad"]
        cambio_actual.estado = estado_anterior["estado"]
        cambio_actual.fecha_cierre = estado_anterior["fecha_cierre"]
        cambio_actual.responsable_id = estado_anterior["responsable_id"]

        id_config_items = [
            uuid.UUID(id_item) for id_item in estado_anterior["id_config_items"]
        ]

        config_items = session.exec(
            select(ItemConfiguracion).where(ItemConfiguracion.id.in_(id_config_items))
        ).all()

        cambio_actual.config_items = config_items

        id_incidentes = [
            uuid.UUID(id_incidente) for id_incidente in estado_anterior["id_incidentes"]
        ]

        incidentes = session.exec(
            select(Incidente).where(Incidente.id.in_(id_incidentes))
        ).all()

        cambio_actual.incidentes = incidentes

        id_problemas = [
            uuid.UUID(id_problema) for id_problema in estado_anterior["id_problemas"]
        ]

        problemas = session.exec(
            select(Problema).where(Problema.id.in_(id_problemas))
        ).all()

        cambio_actual.problemas = problemas

        session.add(cambio_actual)
        session.commit()
        session.refresh(cambio_actual)

        return cambio_actual
