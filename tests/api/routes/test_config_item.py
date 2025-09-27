# ruff: noqa: ARG001

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.config_items import CategoriaItem, EstadoItem
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/config-items"


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
