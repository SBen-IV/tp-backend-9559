import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.config_items import ItemsConfiguracionService as crud
from app.models.config_items import (
    ItemConfiguracionCrear,
    ItemConfiguracionPublico,
)

router = APIRouter(prefix="/config-items")


@router.post("/", response_model=ItemConfiguracionPublico)
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

    return item_configuracion


@router.get("/{id_item_config}", response_model=ItemConfiguracionPublico)
async def get_config_item(
    session: SessionDep, current_user: CurrentUser, id_item_config: uuid.UUID
) -> ItemConfiguracionPublico:
    return crud.get_item_configuracion_by_id(
        session=session, id_item_config=id_item_config
    )
