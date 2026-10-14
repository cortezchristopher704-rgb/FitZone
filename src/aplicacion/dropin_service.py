"""DropInService (Etapa 4) -- US-019, delega en el Domain Service
ServicioDeInscripcionExtraordinaria (no toca la Membresia del socio)."""
from __future__ import annotations

from uuid import UUID

from src.aplicacion.dtos import EstadoReservaDTO, ReservaDTO
from src.dominio.servicios_dominio import ServicioDeInscripcionExtraordinaria
from src.infraestructura.unit_of_work import UnitOfWorkEnMemoria


class DropInService:
    def __init__(self, uow: UnitOfWorkEnMemoria) -> None:
        self._uow = uow
        self._servicio_drop_in = ServicioDeInscripcionExtraordinaria()

    def pagar_acceso_extraordinario(self, socio_id: UUID, clase_id: UUID, monto: float) -> ReservaDTO:
        clase = self._uow.clases.obtener_por_id(clase_id)
        if clase is None:
            return ReservaDTO(estado=EstadoReservaDTO.RECHAZADA, motivo_rechazo="ClaseNoExiste")

        reserva = self._servicio_drop_in.inscribir_drop_in(clase, socio_id, monto)
        self._uow.registrar_cambio(clase)
        self._uow.commit()

        estado_dto = EstadoReservaDTO.CONFIRMADA if reserva.estado.name == "CONFIRMADA" else EstadoReservaDTO.EN_LISTA_ESPERA
        return ReservaDTO(estado=estado_dto, clase_id=clase.id, socio_id=socio_id)
