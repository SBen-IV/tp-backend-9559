import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud.users import UsuariosService as crud
from app.models.users import Rol, UsuarioFilter, UsuarioPublico, UsuarioRegistrar

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

    usuario = crud.create_user(
        session=session,
        usuario_registrar=UsuarioRegistrar.model_validate(usuario_registrar),
    )
    return usuario


@router.get("/me", response_model=UsuarioPublico)
async def get_current_user(current_user: CurrentUser) -> UsuarioPublico:
    return current_user


@router.get("", response_model=list[UsuarioPublico])
async def get_usuarios(
    session: SessionDep, current_user: CurrentUser, rol: Rol | None = None
) -> list[UsuarioPublico]:
    usuario_filter = UsuarioFilter(rol=rol)
    return crud.get_usuarios(session=session, usuario_filter=usuario_filter)


@router.get("/{id_usuario}", response_model=UsuarioPublico)
async def get_problema(
    session: SessionDep, current_user: CurrentUser, id_usuario: uuid.UUID
) -> UsuarioPublico:
    return crud.get_usuario_by_id(session=session, id_usuario=id_usuario)
