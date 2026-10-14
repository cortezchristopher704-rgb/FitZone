"""
Value Objects de FitZone (Etapa 3).

Se definen por sus valores, son inmutables (frozen=True) y no tienen
identidad propia: si "cambian", en realidad se reemplazan por una
instancia nueva (p. ej. extender una Vigencia crea un objeto nuevo,
no muta el existente).
"""
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Vigencia:
    fecha_inicio: datetime
    fecha_fin: datetime

    def es_valida(self, ahora: datetime | None = None) -> bool:
        ahora = ahora or datetime.now(timezone.utc)
        return self.fecha_inicio <= ahora <= self.fecha_fin


@dataclass(frozen=True)
class Horario:
    fecha_hora_inicio: datetime
    duracion_minutos: int


@dataclass(frozen=True)
class Plan:
    """
    tipo: "Basico" | "Premium" | "Ilimitado" (coincide con el glosario N2).
    limite_reservas_simultaneas: regla US-001 / US-013.
    permite_acceso_total: si el plan habilita acceso fisico sin restriccion
    adicional de disciplinas.
    """
    tipo: str
    limite_reservas_simultaneas: int
    permite_acceso_total: bool = True
