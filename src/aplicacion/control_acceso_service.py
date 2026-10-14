"""ControlAccesoService (Etapa 4) -- CU-04."""
from __future__ import annotations

from uuid import UUID

from src.aplicacion.dtos import AccesoResultadoDTO
from src.infraestructura.repositorios import ISocioRepository


class ControlAccesoService:
    def __init__(self, socios: ISocioRepository) -> None:
        self._socios = socios

    def validar_acceso_fisico(self, socio_id: UUID, torniquete_id: str) -> AccesoResultadoDTO:
        """Solo coordina la lectura y la respuesta al torniquete; la regla
        (vigencia de membresia, y que el bloqueo por no-shows NO afecta el
        acceso fisico) vive en Socio.validar_acceso_fisico()."""
        socio = self._socios.obtener_por_id(socio_id)
        if socio is None:
            return AccesoResultadoDTO(permitido=False, motivo="SocioNoExiste")

        permitido = socio.validar_acceso_fisico()
        self._socios.guardar(socio)
        if not permitido:
            return AccesoResultadoDTO(permitido=False, motivo="MembresiaVencida")
        return AccesoResultadoDTO(permitido=True)
