"""AsistenciaService (Etapa 4) -- CU-05, ver Diagrama de secuencia 2."""
from __future__ import annotations

from uuid import UUID

from src.aplicacion.dtos import CommandResult
from src.infraestructura.unit_of_work import UnitOfWorkEnMemoria


class AsistenciaService:
    def __init__(self, uow: UnitOfWorkEnMemoria) -> None:
        self._uow = uow

    def procesar_inasistencia(self, socio_id: UUID, clase_id: UUID) -> CommandResult:
        clase = self._uow.clases.obtener_por_id(clase_id)
        socio = self._uow.socios.obtener_por_id(socio_id)
        if clase is None or socio is None:
            return CommandResult(exito=False, mensaje="SocioOClaseNoExiste")

        clase.registrar_asistencia(socio_id, asistio=False)
        socio.registrar_inasistencia()  # aqui el dominio decide autonomamente si sanciona (Etapa 7, hallazgo #2)

        # el dominio ya decidio si sanciona o no (Socio.evaluar_bloqueo); la
        # capa de aplicacion solo lee el resultado para construir la
        # respuesta, nunca evalua la regla de las 3 inasistencias.
        quedo_sancionado = socio.estado.name == "SANCIONADO"

        self._uow.registrar_cambio(clase)
        self._uow.registrar_cambio(socio)
        self._uow.commit()

        mensaje = "SocioBloqueadoPorInasistencia" if quedo_sancionado else "InasistenciaRegistrada"
        return CommandResult(exito=True, mensaje=mensaje)
