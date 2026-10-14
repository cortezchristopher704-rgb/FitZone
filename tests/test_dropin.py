"""Prueba de US-019 (acceso drop-in) via el Domain Service
ServicioDeInscripcionExtraordinaria, expuesto por DropInService."""
from src.aplicacion.dropin_service import DropInService
from src.aplicacion.dtos import EstadoReservaDTO
from src.infraestructura.unit_of_work import UnitOfWorkEnMemoria
from tests.conftest import crear_clase


def test_dropin_no_modifica_la_membresia_del_socio(repos):
    uow = UnitOfWorkEnMemoria(socios=repos["socios"], clases=repos["clases"])
    servicio = DropInService(uow)
    clase = crear_clase(capacidad=5)
    repos["clases"].guardar(clase)

    from uuid import uuid4

    socio_externo_id = uuid4()  # un drop-in puede ser alguien sin Membresia registrada
    resultado = servicio.pagar_acceso_extraordinario(socio_externo_id, clase.id, monto=150.0)

    assert resultado.estado == EstadoReservaDTO.CONFIRMADA
    clase_guardada = repos["clases"].obtener_por_id(clase.id)
    reserva = next(r for r in clase_guardada.reservas if r.socio_id == socio_externo_id)
    assert reserva.es_drop_in is True
