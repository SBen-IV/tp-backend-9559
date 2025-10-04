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


def test_get_change_by_titulo(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them
    titulo = "Nueva television"

    # When the user gets them by titulo
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    for cambio in cambios:
        assert cambio["titulo"].lower().find(titulo)
        
        
def test_get_change_by_descripcion(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them
    descripcion = "Cambiar la television manual"

    # When the user gets them by description
    r = client.get(f"{BASE_URL}", params={"descripcion": descripcion})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    for cambio in cambios:
        assert cambio["descripcion"].lower().find(descripcion)
        
        
def test_get_change_returns_items(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them
    
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    
    # The change from the seed should have this item linked
    config_item = config_items.json()[0] 

    titulo = "Nueva television"

    # When the user gets them 
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    # And it includes the items linked
    for cambio in cambios:
        item_from_change = cambio["config_items"][0]
        assert cambio["descripcion"].lower().find(titulo)
        assert config_item["nombre"] == item_from_change["nombre"]
        assert config_item["owner_id"] == item_from_change["owner_id"]
        
def test_get_change_by_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    
    # First we need the id of an item
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    
    # The change from the seed should have this item linked
    config_item = config_items.json()[0] 
    
    # Given a new change
    titulo = "Impresora"
    descripcion = "Reemplazar la impresora"
    prioridad = Prioridad.BAJA
    id_config_items = [ config_item['id'] ]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
    change_id = r.json()["id"]

    # When the user gets it by id
    r = client.get(f"{BASE_URL}/{change_id}")

    # Then it returns the same change
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == titulo
    assert cambio["descripcion"] == descripcion
    assert cambio["prioridad"] == prioridad
    assert cambio["fecha_creacion"] > str(now)
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert cambio["owner_id"] 
    assert cambio["config_items"][0]['id'] == config_item['id']    