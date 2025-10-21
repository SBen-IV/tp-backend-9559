import os
import uuid

from app.models.changes import CambioCrear
from app.models.commons import Prioridad
from app.models.config_items import CategoriaItem, ItemConfiguracionCrear
from app.models.incidents import CategoriaIncidente, IncidenteCrear
from app.models.problems import ProblemaCrear
from app.models.users import Rol, UsuarioRegistrar

seed_usuarios = []
seed_items_config = []
seed_cambios = []
seed_incidentes = []
seed_problemas = []

id_user = uuid.uuid4()


if os.getenv("TESTS", None):
    seed_usuarios = [
        UsuarioRegistrar(
            nombre="Alice",
            apellido="Smith",
            email="alice@company.com",
            rol=Rol.EMPLEADO,
            contraseña="12345678",
        ),
        UsuarioRegistrar(
            nombre="Carl",
            apellido="Johnson",
            email="carl@company.com",
            rol=Rol.CLIENTE,
            contraseña="12345678",
        ),
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

    seed_cambios = [
        CambioCrear(
            titulo="Nueva television",
            descripcion="Cambiar la television manual",
            prioridad="BAJA",
            id_config_items=[
                "1" * 32
            ],  # This item ID doesn't exist, it'll be overwritten in core/db.py anyway
        ),
    ]

    seed_incidentes = [
        IncidenteCrear(
            titulo="CPU quemada",
            descripcion="Se quemó la CPU del servidor",
            prioridad=Prioridad.MEDIA,
            categoria=CategoriaIncidente.HARDWARE,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="Contraseñas visibles",
            descripcion="Las contraseñas de los usuarios pueden accederse a través de un hack del frontend",
            prioridad=Prioridad.URGENTE,
            categoria=CategoriaIncidente.SEGURIDAD,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="No se hacen los backups",
            descripcion="La nueva base de datos no está generando backups diarios",
            prioridad=Prioridad.ALTA,
            categoria=CategoriaIncidente.SOFTWARE,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="Acceso a usuarios",
            descripcion="Se solicita un método de acceso a los usuarios en AWS para cumplir auditoría",
            prioridad=Prioridad.BAJA,
            categoria=CategoriaIncidente.SOLICITUD_DE_SERVICIO,
            id_config_items=[],
        ),
    ]

    seed_problemas = [
        ProblemaCrear(
            titulo="No funciona webcam",
            descripcion="Al querer usar la webcam en Zoom me sale en negro",
            prioridad=Prioridad.BAJA,
            id_config_items=[],
            id_incidentes=[],
        ),
        ProblemaCrear(
            titulo="CPU sobrecalentada",
            descripcion="Se sobrecalienta la CPU de mi pc al usar Google Meet",
            prioridad=Prioridad.MEDIA,
            id_config_items=[],
            id_incidentes=[],
        ),
        ProblemaCrear(
            titulo="Servidor lento",
            descripcion="Se sobrecalienta en horas pico",
            prioridad=Prioridad.ALTA,
            id_config_items=[],
            id_incidentes=[],
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
            apellido="Johnson",
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

    seed_incidentes = [
        IncidenteCrear(
            titulo="CPU quemada",
            descripcion="Se quemó la CPU del servidor",
            prioridad=Prioridad.MEDIA,
            categoria=CategoriaIncidente.HARDWARE,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="Contraseñas visibles",
            descripcion="Las contraseñas de los usuarios pueden accederse a través de un hack del frontend",
            prioridad=Prioridad.URGENTE,
            categoria=CategoriaIncidente.SEGURIDAD,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="No se hacen los backups",
            descripcion="La nueva base de datos no está generando backups diarios",
            prioridad=Prioridad.ALTA,
            categoria=CategoriaIncidente.SOFTWARE,
            id_config_items=[],
        ),
        IncidenteCrear(
            titulo="Acceso a usuarios",
            descripcion="Se solicita un método de acceso a los usuarios en AWS para cumplir auditoría",
            prioridad=Prioridad.BAJA,
            categoria=CategoriaIncidente.SOLICITUD_DE_SERVICIO,
            id_config_items=[],
        ),
    ]

    seed_problemas = [
        ProblemaCrear(
            titulo="No funciona webcam",
            descripcion="Al querer usar la webcam en Zoom me sale en negro",
            prioridad=Prioridad.BAJA,
            id_config_items=[],
            id_incidentes=[],
        ),
        ProblemaCrear(
            titulo="CPU sobrecalentada",
            descripcion="Se sobrecalienta la CPU de mi pc al usar Google Meet",
            prioridad=Prioridad.MEDIA,
            id_config_items=[],
            id_incidentes=[],
        ),
        ProblemaCrear(
            titulo="Servidor lento",
            descripcion="Se sobrecalienta en horas pico",
            prioridad=Prioridad.ALTA,
            id_config_items=[],
            id_incidentes=[],
        ),
    ]
