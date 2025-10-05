from .changes import CambioPublico, CambioPublicoConItems
from .config_items import (
    ItemConfiguracionPublico,
    ItemConfiguracionPublicoConCambios,
    ItemConfiguracionPublicoConProblemas,
)
from .problems import ProblemaPublico, ProblemaPublicoConItems
from .users import UsuarioPublico

ItemConfiguracionPublico.model_rebuild()
ItemConfiguracionPublicoConCambios.model_rebuild()
ItemConfiguracionPublicoConProblemas.model_rebuild()
CambioPublicoConItems.model_rebuild()
CambioPublico.model_rebuild()
ProblemaPublicoConItems.model_rebuild()
ProblemaPublico.model_rebuild()
UsuarioPublico.model_rebuild()
