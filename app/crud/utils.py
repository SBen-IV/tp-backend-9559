from sqlmodel import Session, select

from app.models.app_version import AppVersion


class AppVersionService:
    def get_version(session: Session) -> AppVersion:
        version = session.exec(select(AppVersion)).first()
        return version
