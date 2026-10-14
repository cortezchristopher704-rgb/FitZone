"""
Aggregate Socio (Etapa 3 / 3.2 Fichas de Agregados).

Raiz: Socio.
Responsabilidades: autoevaluar elegibilidad para accesos fisicos y
reservas; monitorear cuotas de inasistencias.
Invariantes protegidas:
  1) Un socio posee solo una Membresia activa a la vez.
  2) Si el plan es "Basico", las reservas simultaneas son <= 2.
  3) Acumular 3 no-shows mensuales impone estado "Sancionado" (7 dias).
Eventos emitidos: SocioBloqueadoPorInasistencia, AccesoFisicoDenegado,
MembresiaVencida.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from typing import List
from uuid import UUID, uuid4

from src.dominio.eventos import (
    AccesoFisicoDenegado,
    DomainEvent,
    MembresiaVencida,
    SocioBloqueadoPorInasistencia,
)
from src.dominio.excepciones import MembresiaNoVigenteError, SocioSancionadoError
from src.dominio.value_objects import Plan, Vigencia

UMBRAL_NO_SHOWS_MENSUAL = 3  # ver hallazgo #2 (Etapa 7, principio O): parametrizable
DIAS_SANCION = 7


class EstadoSocio(Enum):
    ACTIVO = auto()
    SANCIONADO = auto()


class EstadoMembresia(Enum):
    ACTIVA = auto()
    VENCIDA = auto()


@dataclass
class Membresia:
    """Entity: tiene identidad y ciclo de vida propio (se renueva, no se recrea)."""

    plan: Plan
    vigencia: Vigencia
    id: UUID = field(default_factory=uuid4)
    estado: EstadoMembresia = EstadoMembresia.ACTIVA

    def esta_vigente(self, ahora: datetime | None = None) -> bool:
        return self.estado == EstadoMembresia.ACTIVA and self.vigencia.es_valida(ahora)


@dataclass
class Socio:
    """Aggregate Root. Unica puerta de entrada para cambiar su propio estado."""

    nombre: str
    contacto: str
    membresia: Membresia
    id: UUID = field(default_factory=uuid4)
    estado: EstadoSocio = EstadoSocio.ACTIVO
    inasistencias_mes: int = 0
    sancion_hasta: datetime | None = None
    _eventos: List[DomainEvent] = field(default_factory=list, repr=False)

    # -- consulta de eventos pendientes (los recoge la capa de aplicacion / UoW) --
    def eventos_pendientes(self) -> List[DomainEvent]:
        return list(self._eventos)

    def limpiar_eventos(self) -> None:
        self._eventos.clear()

    # -- comportamiento de negocio --
    def verificar_vigencia_contractual(self, ahora: datetime | None = None) -> bool:
        """CU-04: valida si la membresia sigue vigente (US-006/US-018)."""
        if not self.membresia.esta_vigente(ahora):
            self._eventos.append(MembresiaVencida(socio_id=self.id))
            return False
        return True

    def puede_reservar(self, reservas_activas_actuales: int, ahora: datetime | None = None) -> None:
        """Lanza una excepcion de dominio si el socio no puede reservar.

        Encapsula las invariantes 1 y 2 del aggregate (vigencia + limite
        por plan), para que ReservaService (aplicacion) nunca evalue
        estas reglas directamente (Etapa 4, revision obligatoria).
        """
        if self.estado == EstadoSocio.SANCIONADO:
            if self.sancion_hasta and ahora and ahora < self.sancion_hasta:
                raise SocioSancionadoError(
                    f"Socio {self.id} sancionado hasta {self.sancion_hasta.isoformat()}"
                )
            if self.sancion_hasta is None:
                raise SocioSancionadoError(f"Socio {self.id} sancionado")
        if not self.verificar_vigencia_contractual(ahora):
            raise MembresiaNoVigenteError(f"Membresia de socio {self.id} no vigente")
        if reservas_activas_actuales >= self.membresia.plan.limite_reservas_simultaneas:
            from src.dominio.excepciones import LimiteReservasSimultaneasError

            raise LimiteReservasSimultaneasError(
                f"Socio {self.id} alcanzo el limite de "
                f"{self.membresia.plan.limite_reservas_simultaneas} reservas simultaneas"
            )

    def validar_acceso_fisico(self, ahora: datetime | None = None) -> bool:
        """CU-04: el bloqueo por no-shows NO afecta el acceso fisico (solo reservas).

        Esto responde directamente a la regla de negocio N4 documentada en
        la Etapa 3: 'el acceso fisico al gimnasio permanece permitido'.
        """
        if not self.verificar_vigencia_contractual(ahora):
            self._eventos.append(
                AccesoFisicoDenegado(socio_id=self.id, motivo="MembresiaVencida")
            )
            return False
        return True

    def registrar_inasistencia(self, ahora: datetime | None = None) -> None:
        """CU-05: registra un no-show y evalua el bloqueo (paso 'EvaluarBloqueo' del
        diagrama de secuencia 2)."""
        self.inasistencias_mes += 1
        self.evaluar_bloqueo(ahora)

    def evaluar_bloqueo(self, ahora: datetime | None = None) -> bool:
        """Devuelve True si el socio quedo sancionado en esta evaluacion."""
        if self.inasistencias_mes >= UMBRAL_NO_SHOWS_MENSUAL and self.estado != EstadoSocio.SANCIONADO:
            ahora = ahora or datetime.now(timezone.utc)
            self.estado = EstadoSocio.SANCIONADO
            self.sancion_hasta = ahora + timedelta(days=DIAS_SANCION)
            self._eventos.append(
                SocioBloqueadoPorInasistencia(socio_id=self.id, dias_bloqueo=DIAS_SANCION)
            )
            return True
        return False

    def reiniciar_ciclo_mensual(self) -> None:
        """Tarea de mantenimiento (fuera del alcance de los CU, pero necesaria
        para que el umbral de no-shows sea mensual y no acumulativo de por vida)."""
        self.inasistencias_mes = 0
        if self.estado == EstadoSocio.SANCIONADO and self.sancion_hasta:
            self.estado = EstadoSocio.ACTIVO if datetime.now(timezone.utc) >= self.sancion_hasta else self.estado
