from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.users import Usuario, UsuarioRegistrar


class UsuarioService:
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
