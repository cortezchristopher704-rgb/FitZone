"""
Domain Events de FitZone (Etapa 3).

Son hechos de negocio ya ocurridos e inmutables. Otros componentes
(NotificacionService, bitacoras, futuros listeners) pueden
suscribirse a ellos sin que el Aggregate que los emite conozca quien
los consume -- asi se evita que ClaseProgramada o Socio dependan de
NotificacionService (principio de inversion de dependencias, ADR-01).
"""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    ocurrido_en: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservaConfirmada(DomainEvent):
    clase_id: UUID = None
    socio_id: UUID = None


@dataclass(frozen=True)
class LugarLiberadoEnClase(DomainEvent):
    clase_id: UUID = None
    socio_promovido_id: UUID | None = None


@dataclass(frozen=True)
class ClaseCanceladaPorInstructor(DomainEvent):
    clase_id: UUID = None
    motivo: str = ""


@dataclass(frozen=True)
class SocioBloqueadoPorInasistencia(DomainEvent):
    socio_id: UUID = None
    dias_bloqueo: int = 7


@dataclass(frozen=True)
class AccesoFisicoDenegado(DomainEvent):
    socio_id: UUID = None
    motivo: str = ""


@dataclass(frozen=True)
class MembresiaVencida(DomainEvent):
    socio_id: UUID = None
