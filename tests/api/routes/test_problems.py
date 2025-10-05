# ruff: noqa: ARG001
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.commons import Prioridad
from app.models.config_items import ItemConfiguracion
from app.models.problems import EstadoProblema
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/problems"


def test_create_new_problema(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema'
    titulo = "BSOD"
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.MEDIA

    id_config_item = session.exec(
        select(ItemConfiguracion).where(ItemConfiguracion.nombre == "Windows")
    ).first()

    # Make sure the config item exists
    assert id_config_item

    id_config_items = [str(id_config_item.id)]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    # When user tries to create the 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    problema = r.json()

    assert problema
    assert problema["titulo"] == titulo
    assert problema["descripcion"] == descripcion
    assert problema["prioridad"] == prioridad
    assert problema["fecha_creacion"] > str(now)
    assert problema["estado"] == EstadoProblema.EN_ANALISIS
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert problema["owner_id"]
    assert problema["responsable_id"] is None
    # And it includes the items linked
    assert len(problema["config_items"]) == len(id_config_items)
    for c in problema["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_problema_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with empty 'titulo'
    titulo = ""
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_problema_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_problema_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with empty 'descripcion'
    titulo = "BSOD"
    descripcion = ""
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"
