# ruff: noqa: ARG001
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.commons import Prioridad
from app.models.config_items import ItemConfiguracion
from app.models.incidents import CategoriaIncidente, EstadoIncidente
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/incidents"


def test_get_all_incidentes(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them

    # When the user gets all incidentes
    r = client.get(f"{BASE_URL}")

    # Then it returns a list of incidentes
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 4


def test_get_incidentes_by_titulo(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them
    titulo = "quemada"

    # When the user gets them by titulo
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of incidentes
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 1

    for incidente in incidentes:
        assert incidente["titulo"].lower().find(titulo)


def test_get_incidente_by_prioridad(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them
    prioridad = "URGENTE"

    # When the user gets them by prioridad
    r = client.get(f"{BASE_URL}", params={"prioridad": prioridad})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 1

    for incidente in incidentes:
        assert incidente["prioridad"].lower().find(prioridad)


#
#
# def test_get_config_item_by_categoria(client: TestClient, session: Session) -> None:
#     # Given some config items
#     # Check db_seed.py to see them
#     categoria = "HARDWARE"
#
#     # When the user gets them by categoria
#     r = client.get(f"{BASE_URL}", params={"categoria": categoria})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     items_config = r.json()
#
#     assert len(items_config) == 1
#
#     for item_config in items_config:
#         assert item_config["categoria"] == categoria
#
#
# def test_get_config_item_by_estado(client: TestClient, session: Session) -> None:
#     # Given some config items
#     # Check db_seed.py to see them
#     estado = "PLANEADO"
#
#     # When the user gets them by estado
#     r = client.get(f"{BASE_URL}", params={"estado": estado})
#
#     # Then it returns a list of config item
#     assert 200 <= r.status_code < 300
#
#     items_config = r.json()
#
#     assert len(items_config) == 3
#
#     for item_config in items_config:
#         assert item_config["estado"] == estado
#
#
# def test_get_config_item_by_id(
#     client: TestClient, session: Session, empleado_token_headers: dict[str, str]
# ) -> None:
#     # Given a new config item
#     nombre = "Linux"
#     descripcion = "Sistema operativo"
#     categoria = CategoriaItem.SOFTWARE
#     version = "Ubuntu"
#
#     now = datetime.now(timezone.utc)
#
#     data = {
#         "nombre": nombre,
#         "descripcion": descripcion,
#         "categoria": categoria,
#         "version": version,
#     }
#
#     r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
#     config_item_id = r.json()["id"]
#
#     # When the user gets it by id
#     r = client.get(f"{BASE_URL}/{config_item_id}")
#
#     # Then it returns the same config item
#     assert 200 <= r.status_code < 300
#
#     item_configuracion = r.json()
#
#     assert item_configuracion
#     assert item_configuracion["nombre"] == nombre
#     assert item_configuracion["descripcion"] == descripcion
#     assert item_configuracion["categoria"] == categoria
#     assert item_configuracion["version"] == version
#     assert item_configuracion["fecha_creacion"] > str(now)
#     assert item_configuracion["estado"] == EstadoItem.PLANEADO
#     # Just check that `owner_id` is present, maybe if a get user
#     # is implemented we can check if it's equal
#     assert item_configuracion["owner_id"]


def test_create_new_incidente(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente'
    titulo = "Base de datos"
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    id_config_item = session.exec(select(ItemConfiguracion)).first()

    # Make sure the config item exists
    assert id_config_item

    id_config_items = [str(id_config_item.id)]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    # When user tries to create the 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    incidente = r.json()

    assert incidente
    assert incidente["titulo"] == titulo
    assert incidente["descripcion"] == descripcion
    assert incidente["categoria"] == categoria
    assert incidente["prioridad"] == prioridad
    assert incidente["fecha_creacion"] > str(now)
    assert incidente["estado"] == EstadoIncidente.NUEVO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert incidente["owner_id"]
    assert incidente["responsable_id"] is None
    # And it includes the items linked
    assert len(incidente["config_items"]) == len(id_config_items)
    for c in incidente["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_incidente_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with empty 'titulo'
    titulo = ""
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_incidente_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_incidente_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with empty 'descripcion'
    titulo = "Base de datos"
    descripcion = ""
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"
