"""Commands de CQRS (Etapa 6): operaciones que cambian el estado del sistema."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelarReservaCommand:
    socio_id: UUID
    clase_id: UUID


@dataclass(frozen=True)
class SancionarPorAusenciaCommand:
    socio_id: UUID
    clase_id: UUID
