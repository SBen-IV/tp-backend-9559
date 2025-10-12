import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.users import Usuario, UsuarioFilter, UsuarioRegistrar


class UsuariosService:
    def create_user(
        *, session: Session, usuario_registrar: UsuarioRegistrar
    ) -> Usuario:
        db_obj = Usuario.model_validate(
            usuario_registrar,
            update={
                "contraseña_hasheada": get_password_hash(usuario_registrar.contraseña)
            },
        )

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

        return db_obj

    def get_user_by_email(*, session: Session, email: str) -> Usuario | None:
        query = select(Usuario).where(Usuario.email == email)
        return session.exec(query).first()

    def authenticate(*, session: Session, email: str, password: str) -> Usuario | None:
        db_user = UsuariosService.get_user_by_email(session=session, email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.contraseña_hasheada):
            return None
        return db_user

    def get_usuarios(
        *, session: Session, usuario_filter: UsuarioFilter
    ) -> list[Usuario]:
        query = select(Usuario)

        if usuario_filter.rol is not None:
            query = query.where(Usuario.rol == usuario_filter.rol)

        return session.exec(query).all()

    def get_usuario_by_id(*, session: Session, id_usuario: uuid.UUID) -> Usuario:
        return session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
