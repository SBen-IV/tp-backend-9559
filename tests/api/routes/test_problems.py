# ruff: noqa: ARG001
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.commons import Prioridad
from app.models.config_items import ItemConfiguracion
from app.models.problems import EstadoProblema
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/problems"


def test_get_all_problemas(client: TestClient, session: Session) -> None:
    # Given some problemas
    # Check db_seed.py to see them

    # When the user gets all problemas
    r = client.get(f"{BASE_URL}")

    # Then it returns a list of problemas
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 3


# def test_get_problemas_by_titulo(client: TestClient, session: Session) -> None:
#     # Given some problemas
#     # Check db_seed.py to see them
#     titulo = "quemada"
#
#     # When the user gets them by titulo
#     r = client.get(f"{BASE_URL}", params={"titulo": titulo})
#
#     # Then it returns a list of problemas
#     assert 200 <= r.status_code < 300
#
#     problemas = r.json()
#
#     assert len(problemas) == 1
#
#     for problema in problemas:
#         assert problema["titulo"].lower().find(titulo)
#
#
# def test_get_problema_by_prioridad(client: TestClient, session: Session) -> None:
#     # Given some problemas
#     # Check db_seed.py to see them
#     prioridad = "URGENTE"
#
#     # When the user gets them by prioridad
#     r = client.get(f"{BASE_URL}", params={"prioridad": prioridad})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     problemas = r.json()
#
#     assert len(problemas) == 1
#
#     for problema in problemas:
#         assert problema["prioridad"].lower().find(prioridad)
#
#
# def test_get_problema_by_categoria(client: TestClient, session: Session) -> None:
#     # Given some config items
#     # Check db_seed.py to see them
#     categoria = "SOLICITUD_DE_SERVICIO"
#
#     # When the user gets them by categoria
#     r = client.get(f"{BASE_URL}", params={"categoria": categoria})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     problemas = r.json()
#
#     assert len(problemas) == 1
#
#     for problema in problemas:
#         assert problema["categoria"] == categoria
#
#
# def test_get_problema_by_estado_nuevo(client: TestClient, session: Session) -> None:
#     # Given some config items
#     # Check db_seed.py to see them
#     estado = "NUEVO"
#
#     # When the user gets them by estado
#     r = client.get(f"{BASE_URL}", params={"estado": estado})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     problemas = r.json()
#
#     assert len(problemas) == 4
#
#     for problema in problemas:
#         assert problema["estado"] == estado
#
#
# def test_get_problema_by_estado_resuelto(client: TestClient, session: Session) -> None:
#     # Given some config items
#     # Check db_seed.py to see them
#     estado = "RESUELTO"
#
#     # When the user gets them by estado
#     r = client.get(f"{BASE_URL}", params={"estado": estado})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     problemas = r.json()
#
#     assert len(problemas) == 0
#
#
# def test_get_problema_by_id(
#     client: TestClient, session: Session, empleado_token_headers: dict[str, str]
# ) -> None:
#     # First we need the id of an item
#     config_items = client.get(f"{settings.API_V1_STR}/config-items")
#
#     config_item = config_items.json()[0]
#
#     # Given a new problema
#     titulo = "Cache falla"
#     descripcion = "Redis falla al traer artículos nuevos"
#     prioridad = Prioridad.MEDIA
#     categoria = Categoriaproblema.SOFTWARE
#     id_config_items = [config_item["id"]]
#
#     now = datetime.now(timezone.utc)
#
#     data = {
#         "titulo": titulo,
#         "descripcion": descripcion,
#         "prioridad": prioridad,
#         "categoria": categoria,
#         "id_config_items": id_config_items,
#     }
#
#     r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
#     problema_id = r.json()["id"]
#
#     # When the user gets it by id
#     r = client.get(f"{BASE_URL}/{problema_id}")
#
#     # Then it returns the same config item
#     assert 200 <= r.status_code < 300
#
#     problema = r.json()
#
#     assert problema
#     assert problema["titulo"] == titulo
#     assert problema["descripcion"] == descripcion
#     assert problema["categoria"] == categoria
#     assert problema["prioridad"] == prioridad
#     assert problema["fecha_creacion"] > str(now)
#     assert problema["estado"] == Estadoproblema.NUEVO
#     # Just check that `owner_id` is present, maybe if a get user
#     # is implemented we can check if it's equal
#     assert problema["owner_id"]


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
