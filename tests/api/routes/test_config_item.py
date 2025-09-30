# ruff: noqa: ARG001

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.config_items import CategoriaItem, EstadoItem
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/config-items"


def test_get_all_config_item(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them

    # When the user gets all config items
    r = client.get(f"{BASE_URL}")

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    items_config = r.json()

    assert len(items_config) == 3


def test_get_config_item_by_nombre(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    nombre = "Windows"

    # When the user gets them by nombre
    r = client.get(f"{BASE_URL}", params={"nombre": nombre})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    items_config = r.json()

    assert len(items_config) == 1

    for item_config in items_config:
        assert item_config["nombre"].lower().find(nombre)


def test_get_config_item_by_version(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    version = "Celeron"

    # When the user gets them by nombre
    r = client.get(f"{BASE_URL}", params={"version": version})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    items_config = r.json()

    assert len(items_config) == 1

    for item_config in items_config:
        assert item_config["version"].lower().find(version)


def test_get_config_item_by_categoria(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    categoria = "HARDWARE"

    # When the user gets them by categoria
    r = client.get(f"{BASE_URL}", params={"categoria": categoria})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    items_config = r.json()

    assert len(items_config) == 1

    for item_config in items_config:
        assert item_config["categoria"] == categoria


def test_get_config_item_by_estado(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    estado = "PLANEADO"

    # When the user gets them by estado
    r = client.get(f"{BASE_URL}", params={"estado": estado})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    items_config = r.json()

    assert len(items_config) == 3

    for item_config in items_config:
        assert item_config["estado"] == estado


def test_get_config_item_by_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a new config item
    nombre = "Linux"
    descripcion = "Sistema operativo"
    categoria = CategoriaItem.SOFTWARE
    version = "Ubuntu"

    now = datetime.now(timezone.utc)

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
    config_item_id = r.json()["id"]

    # When the user gets it by id
    r = client.get(f"{BASE_URL}/{config_item_id}")

    # Then it returns the same config item
    assert 200 <= r.status_code < 300

    item_configuracion = r.json()

    assert item_configuracion
    assert item_configuracion["nombre"] == nombre
    assert item_configuracion["descripcion"] == descripcion
    assert item_configuracion["categoria"] == categoria
    assert item_configuracion["version"] == version
    assert item_configuracion["fecha_creacion"] > str(now)
    assert item_configuracion["estado"] == EstadoItem.PLANEADO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert item_configuracion["owner_id"]


def test_create_new_config_item(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    nombre = "Windows 10"
    descripcion = "Sistema operativo"
    categoria = CategoriaItem.SOFTWARE
    version = "1H25"

    now = datetime.now(timezone.utc)

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    item_configuracion = r.json()

    assert item_configuracion
    assert item_configuracion["nombre"] == nombre
    assert item_configuracion["descripcion"] == descripcion
    assert item_configuracion["categoria"] == categoria
    assert item_configuracion["version"] == version
    assert item_configuracion["fecha_creacion"] > str(now)
    assert item_configuracion["estado"] == EstadoItem.PLANEADO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert item_configuracion["owner_id"]


def test_create_item_configuracion_with_empty_nombre_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'item configuracion' with empty 'nombre'
    nombre = ""
    descripcion = "Sistema operativo"
    categoria = CategoriaItem.SOFTWARE
    version = "1H25"

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    # When user tries to create a 'item configuracion'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "nombre"


def test_create_item_configuracion_with_nombre_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'item configuracion' with too long 'nombre' (256 characters)
    nombre = "This is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long nombreThis is a very long no"
    descripcion = "Sistema operativo"
    categoria = CategoriaItem.SOFTWARE
    version = "1H25"

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    # When user tries to create a 'item configuracion'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "nombre"


def test_create_item_configuracion_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'item configuracion' with empty 'descripcion'
    nombre = "Windows 10"
    descripcion = ""
    categoria = CategoriaItem.SOFTWARE
    version = "1H25"

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    # When user tries to create a 'item configuracion'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"


def test_create_item_configuracion_with_empty_version_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'item configuracion' with empty 'version'
    nombre = "Windows 10"
    descripcion = "Sistema operativo"
    categoria = CategoriaItem.SOFTWARE
    version = ""

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    # When user tries to create a 'item configuracion'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "version"


def test_create_item_configuracion_with_empty_categoria_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'item configuracion' with empty 'categoria'
    nombre = "Windows 10"
    descripcion = "Sistema operativo"
    categoria = ""
    version = "1H25"

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "version": version,
    }

    # When user tries to create a 'item configuracion'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert (
        details["message"]
        == "Input should be 'SOFTWARE', 'HARDWARE' or 'DOCUMENTACION'"
    )
    assert details["field"] == "categoria"
