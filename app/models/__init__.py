from app.models.incidents import (
    IncidentePublico,
    IncidentePublicoConItems,
    IncidentePulicoConProblemas,
)

from .changes import CambioPublico, CambioPublicoConItems, CambioPublicoConRelaciones
from .config_items import (
    ItemConfiguracionPublico,
    ItemConfiguracionPublicoConCambios,
    ItemConfiguracionPublicoConIncidentes,
    ItemConfiguracionPublicoConProblemas,
)
from .problems import (
    ProblemaPublico,
    ProblemaPublicoConIncidentes,
    ProblemaPublicoConItems,
    ProblemaPublicoConRelaciones,
)
from .users import UsuarioPublico

ItemConfiguracionPublico.model_rebuild()
ItemConfiguracionPublicoConCambios.model_rebuild()
ItemConfiguracionPublicoConProblemas.model_rebuild()
ItemConfiguracionPublicoConIncidentes.model_rebuild()
CambioPublicoConItems.model_rebuild()
CambioPublicoConRelaciones.model_rebuild()
CambioPublico.model_rebuild()
ProblemaPublicoConIncidentes.model_rebuild()
ProblemaPublicoConItems.model_rebuild()
ProblemaPublicoConRelaciones.model_rebuild()
ProblemaPublico.model_rebuild()
IncidentePulicoConProblemas.model_rebuild()
IncidentePublicoConItems.model_rebuild()
IncidentePublico.model_rebuild()
UsuarioPublico.model_rebuild()
