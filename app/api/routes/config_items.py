import uuid

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.deps import CurrentUser, SessionDep
from app.crud.audits import AuditoriaService
from app.crud.config_items import ItemsConfiguracionService as crud
from app.models.auditoria import Auditoria, AuditoriaCrear, AuditoriaFilter
from app.models.commons import Operacion, TipoEntidad
from app.models.config_items import (
    CategoriaItem,
    EstadoItem,
    ItemConfiguracionActualizar,
    ItemConfiguracionCrear,
    ItemConfiguracionFilter,
    ItemConfiguracionPublico,
)
from app.models.users import Rol

router = APIRouter(prefix="/config-items")


@router.post("", response_model=ItemConfiguracionPublico)
async def create_config_item(
    session: SessionDep,
    current_user: CurrentUser,
    item_config_in: ItemConfiguracionCrear,
) -> ItemConfiguracionPublico:
    item_config_crear = ItemConfiguracionCrear.model_validate(
        item_config_in, update={"owner_id": current_user.id}
    )

    item_configuracion = crud.create_item_configuracion(
        session=session, item_config_crear=item_config_crear
    )

    auditoria_crear = AuditoriaCrear(
        tipo_entidad=TipoEntidad.CONFIG_ITEM,
        id_entidad=item_configuracion.id,
        operacion=Operacion.CREAR,
        estado_nuevo=jsonable_encoder(item_configuracion),
        actualizado_por=current_user.id,
    )
    AuditoriaService.registrar_operacion(
        session=session, auditoria_crear=auditoria_crear
    )

    return item_configuracion


@router.get("", response_model=list[ItemConfiguracionPublico])
async def get_config_items(
    session: SessionDep,
    nombre: str | None = None,
    version: str | None = None,
    categoria: CategoriaItem | None = None,
    estado: EstadoItem | None = None,
) -> list[ItemConfiguracionPublico]:
    item_config_filter = ItemConfiguracionFilter(
        nombre=nombre, version=version, categoria=categoria, estado=estado
    )
    return crud.get_items_configuracion(
        session=session, item_config_filter=item_config_filter
    )


@router.get("/{id_item_config}", response_model=ItemConfiguracionPublico)
async def get_config_item(
    session: SessionDep, id_item_config: uuid.UUID
) -> ItemConfiguracionPublico:
    return crud.get_item_configuracion_by_id(
        session=session, id_item_config=id_item_config
    )


@router.patch("/{id_item_config}", response_model=ItemConfiguracionPublico)
async def update_change(
    session: SessionDep,
    current_user: CurrentUser,
    id_item_config: uuid.UUID,
    item_config_actualizar: ItemConfiguracionActualizar,
) -> ItemConfiguracionPublico:
    
    item_configuracion = crud.update_item_configuracion(
        session=session,
        id_item_config=id_item_config,
        item_config_actualizar=item_config_actualizar,
    )
    
    auditoria_crear = AuditoriaCrear( 
        tipo_entidad = TipoEntidad.CONFIG_ITEM,
        id_entidad = item_configuracion.id,
        operacion = Operacion.ACTUALIZAR,
        estado_nuevo = jsonable_encoder(item_configuracion),
        actualizado_por = current_user.id
    )
    AuditoriaService.registrar_operacion(session=session, auditoria_crear=auditoria_crear)
    
    return item_configuracion
    
    


@router.delete("/{id_item_config}", response_model=ItemConfiguracionPublico)
async def delete_item_config(
    session: SessionDep, current_user: CurrentUser, id_item_config: uuid.UUID
) -> ItemConfiguracionPublico:
    if current_user.rol != Rol.EMPLEADO:
        raise HTTPException(
            status_code=401,
            detail="Sólo empleados pueden eliminar un ítem de configuración",
        )

    item =  crud.delete_item_configuracion(
        session=session, id_item_config=id_item_config
    )
    
    auditoria_crear = AuditoriaCrear(
        tipo_entidad=TipoEntidad.CONFIG_ITEM,
        id_entidad=item.id,
        operacion=Operacion.ELIMINAR,
        estado_nuevo=jsonable_encoder(item),
        actualizado_por=current_user.id,
    )
    AuditoriaService.registrar_operacion(
        session=session, auditoria_crear=auditoria_crear
    )
    
    return item


@router.get("/{id_item_config}/history", response_model=list[Auditoria])
async def get_history(session: SessionDep, current_user: CurrentUser, id_item_config: uuid.UUID
) -> list[Auditoria]:
    auditoria_filter = AuditoriaFilter(tipo_entidad=TipoEntidad.CONFIG_ITEM, id_entidad=id_item_config)
    
    return AuditoriaService.get_audits(session=session, auditoria_filter=auditoria_filter)


@router.post("/{id_item_config}/rollback", response_model=ItemConfiguracionPublico)
async def rollback_item_config(session: SessionDep, current_user: CurrentUser, id_item_config: uuid.UUID, id_auditoria: uuid.UUID
) -> ItemConfiguracionPublico:
    item = crud.get_item_configuracion_by_id(session=session, id_item_config=id_item_config)
    
    item_rollback = crud.rollback_item_config(
        session=session, 
        id_item_config=id_item_config, 
        id_audit=id_auditoria,
        current_user_id=current_user.id
    )
    
    return item_rollback