import os
import uuid

from app.models.changes import CambioCrear
from app.models.config_items import CategoriaItem, ItemConfiguracionCrear
from app.models.users import Rol, UsuarioRegistrar

seed_usuarios = []
seed_items_config = []
seed_changes = []

id_user = uuid.uuid4()


if os.getenv("TESTS", None):
    seed_usuarios = [
        UsuarioRegistrar(
            nombre="Alice",
            apellido="Smith",
            email="alice@company.com",
            rol=Rol.EMPLEADO,
            contraseña="12345678",
        )
    ]

    seed_items_config = [
        ItemConfiguracionCrear(
            nombre="Windows",
            descripcion="SO",
            version="Vista",
            categoria=CategoriaItem.SOFTWARE,
        ),
        ItemConfiguracionCrear(
            nombre="Intel",
            descripcion="CPU",
            version="Celeron",
            categoria=CategoriaItem.HARDWARE,
        ),
        ItemConfiguracionCrear(
            nombre="TV manual",
            descripcion="Television manual",
            version="1",
            categoria=CategoriaItem.DOCUMENTACION,
        ),
    ]
    
    seed_changes = [
        CambioCrear(
            titulo="Nueva television",
            descripcion="Cambiar la television manual",
            prioridad="BAJA",
            id_config_items=["1" * 32] # This item ID doesn't exist, it'll be overwritten in core/db.py anyway
        ),
    ]    
