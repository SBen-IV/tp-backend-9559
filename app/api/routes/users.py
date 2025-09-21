from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.crud.users import UsuarioService as crud
from app.models.users import UsuarioPublico, UsuarioRegistrar

router = APIRouter(prefix="/users")


@router.post("/signup", response_model=UsuarioPublico)
async def register_user(
    session: SessionDep, usuario_registrar: UsuarioRegistrar
) -> UsuarioPublico:
    usuario = crud.get_user_by_email(session=session, email=usuario_registrar.email)

    if usuario:
        raise HTTPException(
            status_code=400, detail="Ya existe un usuario con ese email"
        )

    usuario = crud.create_user(session=session, usuario_registrar=usuario_registrar)
    return usuario
