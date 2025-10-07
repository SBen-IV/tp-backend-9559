from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud.problems import ProblemasService as crud
from app.models.commons import Prioridad
from app.models.problems import (
    EstadoProblema,
    ProblemaCrear,
    ProblemaFilter,
    ProblemaPublicoConItems,
)

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


@router.get("/", response_model=list[ProblemaPublicoConItems])
async def get_problemas(
    session: SessionDep,
    titulo: str | None = None,
    prioridad: Prioridad | None = None,
    estado: EstadoProblema | None = None,
) -> list[ProblemaPublicoConItems]:
    problema_filter = ProblemaFilter(
        titulo=titulo,
        prioridad=prioridad,
        estado=estado,
    )
    return crud.get_problemas(session=session, problema_filter=problema_filter)


#
#
# @router.get("/{id_problema}", response_model=ProblemaPublicoConItems)
# async def get_problema(
#     session: SessionDep, id_problema: uuid.UUID
# ) -> ProblemaPublicoConItems:
#     return crud.get_problema_by_id(session=session, id_problema=id_problema)
