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
            id_config_items=[
                "1" * 32
            ],  # This item ID doesn't exist, it'll be overwritten in core/db.py anyway
        ),
    ]
else:
    # Create some basic data in case we need to run reset_db
    seed_usuarios = [
        UsuarioRegistrar(
            nombre="Alice",
            apellido="Smith",
            email="alice@company.com",
            rol=Rol.EMPLEADO,
            contraseña="12345678",
        ),
        UsuarioRegistrar(
            nombre="Bob",
            apellido="Smith",
            email="bob@client.com",
            rol=Rol.CLIENTE,
            contraseña="12345678",
        ),
    ]

    seed_items_config = [
        ItemConfiguracionCrear(
            nombre="Windows",
            descripcion="Windows is a product line of proprietary graphical operating systems developed and marketed by Microsoft. It is grouped into families and subfamilies that cater to particular sectors of the computing industry – Windows (unqualified) for a consumer or corporate workstation, Windows Server for a server and Windows IoT for an embedded system. Windows is sold as either a consumer retail product or licensed to third-party hardware manufacturers who sell products bundled with Windows.",
            version="NT 10.0.19045",
            categoria=CategoriaItem.SOFTWARE,
        ),
        ItemConfiguracionCrear(
            nombre="Intel Core",
            descripcion="Intel Core is a line of multi-core (with the exception of Core Solo and Core 2 Solo) central processing units (CPUs) for midrange, embedded, workstation, high-end and enthusiast computer markets marketed by Intel Corporation. These processors displaced the existing mid- to high-end Pentium processors at the time of their introduction, moving the Pentium to the entry level. Identical or more capable versions of Core processors are also sold as Xeon processors for the server and workstation markets.",
            version="Meteor Lake-H",
            categoria=CategoriaItem.HARDWARE,
        ),
        ItemConfiguracionCrear(
            nombre="Manual impresora HP",
            descripcion="Manual de impresora HP LaserJet",
            version="1",
            categoria=CategoriaItem.DOCUMENTACION,
        ),
    ]
