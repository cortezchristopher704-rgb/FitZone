"""Queries de CQRS (Etapa 6): solo lectura, de alto volumen (US-002, US-006).
Nota: ValidarAccesoFisico (CU-04) NO se modela como Query -- es una
lectura puntual de bajo costo y se mantiene como metodo directo de
ControlAccesoService (ver ADR-03)."""
from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class ConsultarDisponibilidadClasesQuery:
    fecha: date
    sucursal_id: str


@dataclass(frozen=True)
class ConsultarEstadoSocioQuery:
    socio_id: UUID
