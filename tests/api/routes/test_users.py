from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import verify_password
from app.models.users import Usuario
from app.utils.config import settings

# ruff: noqa

BASE_URL = f"{settings.API_V1_STR}/users"


def test_create_new_user(client: TestClient, session: Session) -> None:
    nombre = "Bob"
    apellido = "Bib"
    email = "bob@company.com"
    contraseña = "bobby12345"
    rol = "EMPLEADO"

    data = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "contraseña": contraseña,
        "rol": rol,
    }

    r = client.post(f"{BASE_URL}/signup", json=data)

    assert 200 <= r.status_code < 300
    usuario = r.json()
    assert usuario
    assert usuario["nombre"] == nombre
    assert usuario["apellido"] == apellido
    assert usuario["email"] == email
    assert usuario["rol"] == rol

    usuario_query = select(Usuario).where(Usuario.email == email)
    usuario_db: Usuario = session.exec(usuario_query).first()
    assert usuario_db
    assert usuario_db.nombre == nombre
    assert usuario_db.apellido == apellido
    assert usuario_db.rol == rol
    assert verify_password(contraseña, usuario_db.contraseña_hasheada)


def test_create_user_same_email_fails(client: TestClient, session: Session) -> None:
    nombre = "Bob II"
    apellido = "Biby"
    email = "bob@company.com"
    contraseña = "12345bobby"
    rol = "EMPLEADO"

    data = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "contraseña": contraseña,
        "rol": rol,
    }

    r = client.post(f"{BASE_URL}/signup", json=data)

    assert 400 <= r.status_code < 500
    assert r.json()["detail"] == "Ya existe un usuario con ese email"


def test_create_user_validate_password_too_short(
    client: TestClient, session: Session
) -> None:
    nombre = "Bob Jr"
    apellido = "Boy"
    email = "bobjr@company.com"
    contraseña = "12345"
    rol = "EMPLEADO"

    data = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "contraseña": contraseña,
        "rol": rol,
    }

    r = client.post(f"{BASE_URL}/signup", json=data)

    assert 400 <= r.status_code < 500
    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 8 characters"
    assert details['field'] == "contraseña"


def test_create_user_validate_password_too_long(
    client: TestClient, session: Session
) -> None:
    nombre = "Bob Jr"
    apellido = "Boy"
    email = "bobjr@company.com"
    contraseña = "1231231231231231231231231231231231231231231"
    rol = "EMPLEADO"

    data = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "contraseña": contraseña,
        "rol": rol,
    }

    r = client.post(f"{BASE_URL}/signup", json=data)

    assert 400 <= r.status_code < 500
    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 40 characters"
    assert details['field'] == "contraseña"
