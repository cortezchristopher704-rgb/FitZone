"""
DTOs / resultados de la capa de aplicacion (Etapa 4 y 6).

Traducen excepciones de dominio a resultados de negocio legibles,
sin filtrar detalles tecnicos hacia quien consume el servicio (CLI,
API, pruebas).
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID


class EstadoReservaDTO(Enum):
    CONFIRMADA = auto()
    EN_LISTA_ESPERA = auto()
    RECHAZADA = auto()


@dataclass
class ReservaDTO:
    estado: EstadoReservaDTO
    clase_id: Optional[UUID] = None
    socio_id: Optional[UUID] = None
    posicion_en_espera: Optional[int] = None
    motivo_rechazo: Optional[str] = None


@dataclass
class AccesoResultadoDTO:
    permitido: bool
    motivo: Optional[str] = None


@dataclass
class CommandResult:
    exito: bool
    mensaje: str = ""
    socio_promovido_id: Optional[UUID] = None
