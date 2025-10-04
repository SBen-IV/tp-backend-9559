# ruff: noqa: ARG001
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.changes import Cambio, CambioPublico, EstadoCambio, Prioridad
from app.models.config_items import ItemConfiguracion, ItemConfiguracionPublico
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/changes"


def test_create_new_cambio(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    titulo = "Upgrade CPU of server"
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE

    now = datetime.now(timezone.utc)
    
    config_items = session.exec(select(ItemConfiguracion))
    id_config_items = [str(config_item.id) for config_item in config_items]

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad, "id_config_items": id_config_items}

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == titulo
    assert cambio["descripcion"] == descripcion
    assert cambio["prioridad"] == prioridad
    assert cambio["fecha_creacion"] > str(now)
    assert cambio["estado"] == EstadoCambio.RECIBIDO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert cambio["owner_id"]


def test_create_cambio_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with empty 'titulo'
    titulo = ""
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_cambio_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_cambio_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with empty 'descripcion'
    titulo = "Windows update"
    descripcion = ""
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"
