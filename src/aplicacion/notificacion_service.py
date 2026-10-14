"""NotificacionService (Etapa 7, hallazgo #1): se extrajo de ReservaService
para que cada clase tenga una sola razon para cambiar (principio S)."""
from __future__ import annotations

from uuid import UUID


class NotificacionService:
    def notificar_promocion_lista_espera(self, socio_id: UUID, clase_id: UUID) -> None:
        # En un sistema real esto enviaria un correo/push (US-005: 30 min
        # para confirmar). Aqui queda como punto de integracion explicito.
        print(f"[Notificacion] Socio {socio_id}: tienes 30 minutos para confirmar tu lugar en la clase {clase_id}.")
