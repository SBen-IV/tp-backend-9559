from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.incidents import IncidentesService as crud
from app.models.incidents import IncidenteCrear, IncidentePublicoConItems

router = APIRouter(prefix="/incidents")


@router.post("/", response_model=IncidentePublicoConItems)
async def create_incidente(
    session: SessionDep, current_user: CurrentUser, incidente_in: IncidenteCrear
) -> IncidentePublicoConItems:
    incidente_crear = IncidenteCrear.model_validate(
        incidente_in, update={"owner_id": current_user.id}
    )

    incidente = crud.create_incidente(session=session, incidente_crear=incidente_crear)

    return incidente
