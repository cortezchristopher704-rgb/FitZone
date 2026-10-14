"""
Aggregate ClaseProgramada (Etapa 3 / 3.2 Fichas de Agregados).

Raiz: ClaseProgramada (unica interfaz para interactuar con reservas
de la sesion).
Responsabilidades: aceptar o rechazar reservas segun cupo; coordinar
liberaciones y reasignaciones FIFO de la lista de espera.
Invariantes protegidas:
  1) Las reservas activas nunca superan numericamente la CapacidadMaxima.
  2) El orden de promocion en ListaDeEspera es estrictamente FIFO, sin
     excepciones comerciales.
Eventos emitidos: ReservaConfirmada, LugarLiberadoEnClase,
ClaseCanceladaPorInstructor.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Deque, List, Optional
from uuid import UUID, uuid4

from src.dominio.eventos import (
    ClaseCanceladaPorInstructor,
    DomainEvent,
    LugarLiberadoEnClase,
    ReservaConfirmada,
)
from src.dominio.excepciones import CapacidadExcedidaError, ReservaNoEncontradaError
from src.dominio.instructor import Instructor
from src.dominio.value_objects import Horario


class EstadoReserva(Enum):
    CONFIRMADA = auto()
    EN_LISTA_ESPERA = auto()
    CANCELADA = auto()


class EstadoClase(Enum):
    PROGRAMADA = auto()
    CANCELADA = auto()


@dataclass
class Reserva:
    """Entity (no Aggregate Root): solo existe dentro del limite de
    consistencia de ClaseProgramada, nunca se persiste ni se referencia
    de forma independiente (ver 'Decisiones dudosas o descartadas',
    Etapa 3.3)."""

    socio_id: UUID
    fecha_reserva: datetime = field(default_factory=datetime.utcnow)
    estado: EstadoReserva = EstadoReserva.CONFIRMADA
    es_drop_in: bool = False  # hallazgo #3 (Etapa 7, principio L): atributo en vez de subtipo
    id: UUID = field(default_factory=uuid4)

    def confirmar(self) -> None:
        self.estado = EstadoReserva.CONFIRMADA

    def cancelar(self) -> None:
        self.estado = EstadoReserva.CANCELADA


@dataclass
class ListaDeEspera:
    """Entity administrada exclusivamente por ClaseProgramada. Orden FIFO
    estricto (invariante #2 del aggregate)."""

    socios: Deque[UUID] = field(default_factory=deque)

    def agregar_socio(self, socio_id: UUID) -> int:
        """US-003/US-005: agrega en orden de llegada y devuelve la posicion asignada."""
        self.socios.append(socio_id)
        return len(self.socios)

    def promover_socio(self) -> Optional[UUID]:
        """Devuelve el siguiente socio en FIFO, o None si la lista esta vacia."""
        if not self.socios:
            return None
        return self.socios.popleft()

    def __len__(self) -> int:
        return len(self.socios)


@dataclass
class ClaseProgramada:
    """Aggregate Root."""

    horario: Horario
    capacidad_maxima: int
    instructor: Instructor
    id: UUID = field(default_factory=uuid4)
    estado: EstadoClase = EstadoClase.PROGRAMADA
    reservas: List[Reserva] = field(default_factory=list)
    lista_espera: ListaDeEspera = field(default_factory=ListaDeEspera)
    _eventos: List[DomainEvent] = field(default_factory=list, repr=False)

    def eventos_pendientes(self) -> List[DomainEvent]:
        return list(self._eventos)

    def limpiar_eventos(self) -> None:
        self._eventos.clear()

    @property
    def reservas_activas(self) -> List[Reserva]:
        return [r for r in self.reservas if r.estado == EstadoReserva.CONFIRMADA]

    @property
    def cupo_disponible(self) -> int:
        return self.capacidad_maxima - len(self.reservas_activas)

    def tiene_cupo(self) -> bool:
        return self.cupo_disponible > 0

    # -- CU-01 / CU-02 (diagrama de secuencia 1) --
    def reservar_lugar(self, socio_id: UUID, es_drop_in: bool = False) -> Reserva:
        """Invariante #1: nunca se supera capacidad_maxima.
        Si hay cupo -> confirma. Si no -> delega a lista de espera (CU-02)."""
        if self.tiene_cupo():
            reserva = Reserva(socio_id=socio_id, estado=EstadoReserva.CONFIRMADA, es_drop_in=es_drop_in)
            self.reservas.append(reserva)
            self._eventos.append(ReservaConfirmada(clase_id=self.id, socio_id=socio_id))
            return reserva

        reserva = Reserva(socio_id=socio_id, estado=EstadoReserva.EN_LISTA_ESPERA, es_drop_in=es_drop_in)
        self.reservas.append(reserva)
        self.lista_espera.agregar_socio(socio_id)
        return reserva

    # -- CU-03 (diagrama de secuencia 1, segunda mitad) --
    def cancelar_reserva(self, socio_id: UUID) -> Optional[UUID]:
        """Libera el lugar del socio y promueve automaticamente al primero
        de la lista de espera (orden FIFO, invariante #2).

        Devuelve el id del socio promovido, o None si no habia nadie en espera.
        Este metodo es exactamente el limite transaccional que describe el
        Unit of Work de la Etapa 5 (liberar + promover en una sola operacion).
        """
        reserva = next(
            (r for r in self.reservas if r.socio_id == socio_id and r.estado == EstadoReserva.CONFIRMADA),
            None,
        )
        if reserva is None:
            raise ReservaNoEncontradaError(f"Socio {socio_id} no tiene reserva activa en clase {self.id}")

        reserva.cancelar()
        socio_promovido = self.lista_espera.promover_socio()
        if socio_promovido is not None:
            nueva_reserva = next(
                (r for r in self.reservas if r.socio_id == socio_promovido and r.estado == EstadoReserva.EN_LISTA_ESPERA),
                None,
            )
            if nueva_reserva is not None:
                nueva_reserva.confirmar()
            self._eventos.append(
                LugarLiberadoEnClase(clase_id=self.id, socio_promovido_id=socio_promovido)
            )
        return socio_promovido

    # -- CU-05 (lo invoca AsistenciaService) --
    def registrar_asistencia(self, socio_id: UUID, asistio: bool) -> None:
        """Solo deja constancia en la clase; la sancion del socio vive en el
        Aggregate Socio (Socio.registrar_inasistencia), no aqui -- limite de
        consistencia correcto segun la Etapa 3.3."""
        if not asistio:
            # Punto de extension: aqui se podria registrar en un historial de
            # asistencia por clase si el negocio lo pidiera en el futuro.
            pass

    def cancelar_por_instructor(self, motivo: str) -> None:
        """US-010: cancelacion de clase por el instructor; emite evento de
        dominio para que la capa de aplicacion notifique a los inscritos."""
        self.estado = EstadoClase.CANCELADA
        self._eventos.append(ClaseCanceladaPorInstructor(clase_id=self.id, motivo=motivo))
