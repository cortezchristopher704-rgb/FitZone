"""
Domain Service: ServicioDeInscripcionExtraordinaria (Etapa 3).

Comportamiento que no pertenece naturalmente a una sola entidad: el
acceso "drop-in" (US-019) involucra un pago externo que NO debe
modificar la Membresia del socio (eso romperia el invariante "un
socio posee solo una Membresia activa a la vez"). Por eso vive como
Domain Service apatrida en lugar de como metodo de Socio o de
ClaseProgramada.
"""
from __future__ import annotations

from uuid import UUID

from src.dominio.clase_programada import ClaseProgramada, Reserva


class ServicioDeInscripcionExtraordinaria:
    """Sin estado propio (stateless) -- no es Entity ni Aggregate."""

    def inscribir_drop_in(self, clase: ClaseProgramada, socio_id: UUID, monto_pagado: float) -> Reserva:
        if monto_pagado <= 0:
            raise ValueError("El acceso drop-in requiere un pago mayor a 0")
        return clase.reservar_lugar(socio_id, es_drop_in=True)
