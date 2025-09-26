from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.changes import CambiosService as crud
from app.models.changes import CambioCrear, CambioPublico

router = APIRouter(prefix="/changes")


@router.post("/", response_model=CambioPublico)
async def create_change(
    session: SessionDep, current_user: CurrentUser, cambio_in: CambioCrear
) -> CambioPublico:
    cambio_crear = CambioCrear.model_validate(
        cambio_in, update={"owner_id": current_user.id}
    )

    cambio = crud.create_cambio(session=session, cambio_crear=cambio_crear)

    return cambio
