
from datetime import datetime, timezone

from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.config_items import CategoriaItem, EstadoItem
from app.models.auditoria import Auditoria
from app.utils.config import settings
from app.models.commons import TipoEntidad, Accion

Faker.seed(0)
fake = Faker()

CONFIG_ITEMS_URL = f"{settings.API_V1_STR}/config-items"
AUDITS_URL = f"{settings.API_V1_STR}/audits"


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
    
    auditoria = r.json()[0]
    
    assert auditoria
    assert auditoria["tipo_entidad"] == TipoEntidad.CONFIG_ITEM
    assert auditoria["operacion"] == Accion.CREAR
    assert auditoria["estado_nuevo"]["nombre"] == nombre
    assert auditoria["estado_nuevo"]["descripcion"] == descripcion
    assert auditoria["estado_nuevo"]["version"] == version
    