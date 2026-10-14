"""
ReservaService (Etapa 4).

Coordina CU-01/CU-02 (ReservarClase) y CU-03 (CancelarReserva). No
evalua ninguna regla de negocio directamente -- todas las decisiones
(cupo, FIFO, vigencia, limite de reservas) viven en los Aggregates
ClaseProgramada y Socio. Este servicio solo: recibe la solicitud,
obtiene los objetos, invoca el dominio, persiste con el Unit of Work
y traduce el resultado a un DTO.
"""
from __future__ import annotations

from uuid import UUID

from src.aplicacion.dtos import CommandResult, EstadoReservaDTO, ReservaDTO
from src.dominio.clase_programada import EstadoReserva
from src.dominio.excepciones import DominioError
from src.infraestructura.unit_of_work import UnitOfWorkEnMemoria


class ReservaService:
    def __init__(self, uow: UnitOfWorkEnMemoria) -> None:
        self._uow = uow

    def reservar_clase(self, socio_id: UUID, clase_id: UUID) -> ReservaDTO:
        """CU-01 / CU-02 -- ver Diagrama de secuencia 1."""
        socio = self._uow.socios.obtener_por_id(socio_id)
        clase = self._uow.clases.obtener_por_id(clase_id)
        if socio is None or clase is None:
            return ReservaDTO(estado=EstadoReservaDTO.RECHAZADA, motivo_rechazo="SocioOClaseNoExiste")

        # El limite de reservas simultaneas (US-001/US-013) es por SOCIO a
        # traves de todas sus clases, no por clase individual -- por eso se
        # cuenta recorriendo todas las ClaseProgramada del repositorio en
        # vez de usar clase.reservas_activas (que solo cuenta esta clase).
        reservas_activas_del_socio = sum(
            1
            for c in self._uow.clases.listar_todas()
            for r in c.reservas_activas
            if r.socio_id == socio_id
        )
        try:
            socio.puede_reservar(reservas_activas_del_socio)
        except DominioError as err:
            return ReservaDTO(estado=EstadoReservaDTO.RECHAZADA, motivo_rechazo=str(err))

        reserva = clase.reservar_lugar(socio_id)
        self._uow.registrar_cambio(clase)
        self._uow.commit()

        if reserva.estado == EstadoReserva.CONFIRMADA:
            return ReservaDTO(estado=EstadoReservaDTO.CONFIRMADA, clase_id=clase.id, socio_id=socio_id)
        return ReservaDTO(
            estado=EstadoReservaDTO.EN_LISTA_ESPERA,
            clase_id=clase.id,
            socio_id=socio_id,
            posicion_en_espera=len(clase.lista_espera),
        )

    def cancelar_reserva(self, socio_id: UUID, clase_id: UUID) -> CommandResult:
        """CU-03 -- libera el lugar y promueve FIFO dentro de un mismo
        Unit of Work (ADR-02)."""
        clase = self._uow.clases.obtener_por_id(clase_id)
        if clase is None:
            return CommandResult(exito=False, mensaje="ClaseNoExiste")

        try:
            socio_promovido = clase.cancelar_reserva(socio_id)
        except DominioError as err:
            self._uow.rollback()
            return CommandResult(exito=False, mensaje=str(err))

        self._uow.registrar_cambio(clase)
        self._uow.commit()
        return CommandResult(exito=True, mensaje="ReservaCancelada", socio_promovido_id=socio_promovido)
