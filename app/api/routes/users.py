from fastapi import APIRouter

from app.api.deps import SessionDep
from app.crud.users import UsuarioService as crud
from app.models.users import UsuarioPublico, UsuarioRegistrar

router = APIRouter(prefix="/users")


@router.post("/signup", response_model=UsuarioPublico)
async def register_user(
    session: SessionDep, usuario_registrar: UsuarioRegistrar
) -> UsuarioPublico:
    usuario = crud.create_user(session=session, usuario_registrar=usuario_registrar)
    return usuario
