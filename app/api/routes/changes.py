from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.changes import CambiosService as crud
from app.models.changes import CambioCrear, CambioPublicoConItems

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublicoConItems)
async def create_change(
    session: SessionDep, current_user: CurrentUser, cambio_in: CambioCrear
) -> CambioPublicoConItems:
    cambio_crear = CambioCrear.model_validate(
        cambio_in, update={"owner_id": current_user.id}
    )

    cambio = crud.create_cambio(session=session, cambio_crear=cambio_crear)

    return cambio
