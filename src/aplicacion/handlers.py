"""
Handlers de CQRS (Etapa 6): un handler por Command/Query, cada uno con
sus propias dependencias explicitas (principio I: nadie depende de
metodos que no usa).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.aplicacion.commands import CancelarReservaCommand, SancionarPorAusenciaCommand
from src.aplicacion.dtos import CommandResult
from src.aplicacion.queries import ConsultarDisponibilidadClasesQuery, ConsultarEstadoSocioQuery
from src.aplicacion.reserva_service import ReservaService
from src.aplicacion.asistencia_service import AsistenciaService
from src.infraestructura.repositorios import IClaseProgramadaRepository, ISocioRepository


@dataclass
class ClaseDisponibleDTO:
    clase_id: str
    horario: str
    cupo_disponible: int


@dataclass
class PerfilSocioDTO:
    socio_id: str
    estado: str
    membresia_vigente: bool


class CancelarReservaHandler:
    def __init__(self, reserva_service: ReservaService) -> None:
        self._reserva_service = reserva_service

    def manejar(self, cmd: CancelarReservaCommand) -> CommandResult:
        return self._reserva_service.cancelar_reserva(cmd.socio_id, cmd.clase_id)


class SancionarPorAusenciaHandler:
    def __init__(self, asistencia_service: AsistenciaService) -> None:
        self._asistencia_service = asistencia_service

    def manejar(self, cmd: SancionarPorAusenciaCommand) -> CommandResult:
        return self._asistencia_service.procesar_inasistencia(cmd.socio_id, cmd.clase_id)


class ConsultarDisponibilidadClasesHandler:
    """Lectura de alto volumen: NO carga el Aggregate ClaseProgramada
    completo, solo los campos necesarios para la vista (ADR-03)."""

    def __init__(self, clases: IClaseProgramadaRepository) -> None:
        self._clases = clases

    def manejar(self, query: ConsultarDisponibilidadClasesQuery) -> list[ClaseDisponibleDTO]:
        resultado = []
        for clase in self._clases.listar_todas():
            resultado.append(
                ClaseDisponibleDTO(
                    clase_id=str(clase.id),
                    horario=clase.horario.fecha_hora_inicio.isoformat(),
                    cupo_disponible=clase.cupo_disponible,
                )
            )
        return resultado


class ConsultarEstadoSocioHandler:
    def __init__(self, socios: ISocioRepository) -> None:
        self._socios = socios

    def manejar(self, query: ConsultarEstadoSocioQuery) -> PerfilSocioDTO | None:
        socio = self._socios.obtener_por_id(query.socio_id)
        if socio is None:
            return None
        return PerfilSocioDTO(
            socio_id=str(socio.id),
            estado=socio.estado.name,
            membresia_vigente=socio.membresia.esta_vigente(),
        )
