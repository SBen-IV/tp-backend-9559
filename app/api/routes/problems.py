from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.problems import ProblemasService as crud
from app.models.problems import ProblemaCrear, ProblemaPublicoConItems

router = APIRouter(prefix="/problems")


@router.post("/", response_model=ProblemaPublicoConItems)
async def create_problema(
    session: SessionDep, current_user: CurrentUser, problema_in: ProblemaCrear
) -> ProblemaPublicoConItems:
    problema_crear = ProblemaCrear.model_validate(
        problema_in, update={"owner_id": current_user.id}
    )

    problema = crud.create_problema(session=session, problema_crear=problema_crear)

    return problema
