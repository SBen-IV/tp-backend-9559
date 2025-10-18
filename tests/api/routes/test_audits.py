
from datetime import datetime, timezone

import pytest

from app.models.incidents import CategoriaIncidente
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.config_items import CategoriaItem, EstadoItem
from app.models.auditoria import Auditoria
from app.utils.config import settings
from app.models.commons import Prioridad, TipoEntidad, Operacion

Faker.seed(0)
fake = Faker()

CONFIG_ITEMS_URL = f"{settings.API_V1_STR}/config-items"
AUDITS_URL = f"{settings.API_V1_STR}/audits"
INCIDENTS_URL = f"{settings.API_V1_STR}/incidents"
PROBLEMS_URL = f"{settings.API_V1_STR}/problems"
CHANGES_URL = f"{settings.API_V1_STR}/changes"

def create_random_cambio(client: TestClient, token_headers: dict[str, str]) -> dict:
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(CHANGES_URL, json=data, headers=token_headers)
    return r.json()


def create_random_item_configuracion(
    client: TestClient, token_headers: dict[str, str]
) -> dict:
    nombre = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    version = "1.0"
    categoria = "SOFTWARE"

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "version": version,
        "categoria": categoria,
    }

    r = client.post(CONFIG_ITEMS_URL, json=data, headers=token_headers)
    return r.json()


def create_random_incident(client: TestClient, token_headers: dict[str, str]) -> dict:
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    categoria = CategoriaIncidente.SOFTWARE
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "categoria": categoria,
        "id_config_items": id_config_items,
    }

    r = client.post(INCIDENTS_URL, json=data, headers=token_headers)
    return r.json()


def test_creating_item_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    nombre = "Ubuntu"
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

    r = client.post(CONFIG_ITEMS_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300
    
    r = client.get(AUDITS_URL, headers=empleado_token_headers)
    
    assert 200 <= r.status_code < 300
    
    assert len(r.json()) >= 1
    
    auditoria = r.json()[0]
    
    assert auditoria
    assert auditoria["tipo_entidad"] == TipoEntidad.CONFIG_ITEM
    assert auditoria["operacion"] == Operacion.CREAR
    assert auditoria["estado_nuevo"]["nombre"] == nombre
    assert auditoria["estado_nuevo"]["descripcion"] == descripcion
    assert auditoria["estado_nuevo"]["version"] == version
    
    
def test_creating_incident_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    config_items = client.get(CONFIG_ITEMS_URL)
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    categoria = CategoriaIncidente.SOFTWARE
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "categoria": categoria,
        "id_config_items": id_config_items,
    }

    r = client.post(INCIDENTS_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300
    
    incidente = r.json()
    
    r = client.get(AUDITS_URL, headers=empleado_token_headers, params={"tipo_entidad": TipoEntidad.INCIDENTE.value, "id_entidad": incidente["id"]})
    
    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == incidente["id"]),
        None
    )
    
    assert auditoria
    assert auditoria["tipo_entidad"] == TipoEntidad.INCIDENTE
    assert auditoria["operacion"] == Operacion.CREAR
    assert auditoria["estado_nuevo"]["titulo"] == titulo
    assert auditoria["estado_nuevo"]["descripcion"] == descripcion
    assert auditoria["estado_nuevo"]["prioridad"] == prioridad


def test_creating_problem_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    config_items = client.get(CONFIG_ITEMS_URL)
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(PROBLEMS_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300
    
    incidente = r.json()
    
    r = client.get(AUDITS_URL, headers=empleado_token_headers, params={"tipo_entidad": TipoEntidad.PROBLEMA.value, "id_entidad": incidente["id"]})
    
    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == incidente["id"]),
        None
    )
    
    assert auditoria
    assert auditoria["tipo_entidad"] == TipoEntidad.PROBLEMA.value
    assert auditoria["operacion"] == Operacion.CREAR
    assert auditoria["estado_nuevo"]["titulo"] == titulo
    assert auditoria["estado_nuevo"]["descripcion"] == descripcion
    assert auditoria["estado_nuevo"]["prioridad"] == prioridad
    
    
def test_creating_change_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    config_items = client.get(CONFIG_ITEMS_URL)
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(CHANGES_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300
    
    incidente = r.json()
    
    r = client.get(AUDITS_URL, headers=empleado_token_headers, params={"tipo_entidad": TipoEntidad.CAMBIO.value, "id_entidad": incidente["id"]})
    
    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == incidente["id"]),
        None
    )
    
    assert auditoria
    assert auditoria["tipo_entidad"] == TipoEntidad.CAMBIO.value
    assert auditoria["operacion"] == Operacion.CREAR
    assert auditoria["estado_nuevo"]["titulo"] == titulo
    assert auditoria["estado_nuevo"]["descripcion"] == descripcion
    assert auditoria["estado_nuevo"]["prioridad"] == prioridad
    
    
def test_updating_change_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    cambio_created = create_random_cambio(client, empleado_token_headers)
    
    data = {"titulo": "Nuevo titulo"}

    # When the user edits it
    r = client.patch(
        f"{CHANGES_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()
    
    r = client.get(AUDITS_URL, params={"tipo_entidad": TipoEntidad.CAMBIO.value, "id_entidad": cambio["id"]})

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == cambio["id"]),
        None
    )
    
    assert auditoria
    assert auditoria['id_entidad'] == cambio['id']
    assert auditoria['tipo_entidad'] == TipoEntidad.CAMBIO.value
    assert auditoria['operacion'] == Operacion.ACTUALIZAR.value
    assert auditoria['estado_nuevo']['titulo'] != cambio_created['titulo'] 
    
    
def test_updating_item_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    item_created = create_random_item_configuracion(client, empleado_token_headers)
    
    data = {"nombre": "Nuevo nombre"}

    # When the user edits it
    r = client.patch(
        f"{CONFIG_ITEMS_URL}/{item_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    item = r.json()
    
    r = client.get(AUDITS_URL, params={"tipo_entidad": TipoEntidad.CONFIG_ITEM.value, "id_entidad": item["id"]})

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == item["id"]),
        None
    )
    
    assert auditoria
    assert auditoria['id_entidad'] == item['id']
    assert auditoria['tipo_entidad'] == TipoEntidad.CONFIG_ITEM.value
    assert auditoria['operacion'] == Operacion.ACTUALIZAR.value
    assert auditoria['estado_nuevo']['nombre'] != item_created['nombre'] 
    
    
def test_updating_incident_creates_audit(client: TestClient, session: Session, empleado_token_headers: dict[str, str]) -> None:
    item_created = create_random_incident(client, empleado_token_headers)
    
    data = {"titulo": "Nuevo titulo"}

    # When the user edits it
    r = client.patch(
        f"{INCIDENTS_URL}/{item_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    item = r.json()
    
    r = client.get(AUDITS_URL, params={"tipo_entidad": TipoEntidad.INCIDENTE.value, "id_entidad": item["id"]})

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert len(auditorias) >= 1
    
    auditoria = next(
        (audit for audit in auditorias if audit["id_entidad"] == item["id"]),
        None
    )
    
    assert auditoria
    assert auditoria['id_entidad'] == item['id']
    assert auditoria['tipo_entidad'] == TipoEntidad.INCIDENTE.value
    assert auditoria['operacion'] == Operacion.ACTUALIZAR.value
    assert auditoria['estado_nuevo']['titulo'] != item_created['titulo'] 