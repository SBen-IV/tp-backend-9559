from enum import Enum


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"
    

class TipoEntidad(str, Enum):
  CONFIG_ITEM = "CONFIG_ITEM"
  INCIDENTE = "INCIDENTE"
  CAMBIO = "CAMBIO"
  PROBLEMA = "PROBLEMA"
  
  
class Accion(str, Enum):
  CREAR = "CREAR"
  ACTUALIZAR = "ACTUALIZAR"
  ELIMINAR = "ELIMINAR"
