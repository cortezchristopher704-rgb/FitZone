"""
Excepciones del dominio de FitZone.

Todas heredan de DominioError para que la capa de aplicacion pueda
traducirlas a resultados de negocio (ver aplicacion/dtos.py) sin
depender de detalles tecnicos. Esto responde a la pregunta de la
Etapa 4 (revision obligatoria): "Los errores del dominio pueden
explicarse con terminos del negocio?"
"""


class DominioError(Exception):
    """Error base de reglas de negocio del dominio FitZone."""


class CapacidadExcedidaError(DominioError):
    """La clase no tiene cupo disponible (invariante de ClaseProgramada)."""


class MembresiaNoVigenteError(DominioError):
    """La membresia del socio no esta vigente (invariante de Socio)."""


class SocioSancionadoError(DominioError):
    """El socio esta sancionado y no puede reservar (invariante de Socio)."""


class ReservaNoEncontradaError(DominioError):
    """No existe una reserva activa del socio en la clase indicada."""


class LimiteReservasSimultaneasError(DominioError):
    """El socio supero el limite de reservas simultaneas de su plan."""
