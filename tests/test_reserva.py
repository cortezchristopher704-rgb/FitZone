"""
Pruebas de CU-01, CU-02 y CU-03 -- corresponden exactamente al
Diagrama de secuencia 1 (flujo principal) de la Etapa 8.
"""
from src.aplicacion.dtos import EstadoReservaDTO
from tests.conftest import crear_clase, crear_socio


def test_cu01_reservar_clase_con_cupo_disponible(reserva_service, repos):
    socio = crear_socio()
    clase = crear_clase(capacidad=1)
    repos["socios"].guardar(socio)
    repos["clases"].guardar(clase)

    resultado = reserva_service.reservar_clase(socio.id, clase.id)

    assert resultado.estado == EstadoReservaDTO.CONFIRMADA
    clase_guardada = repos["clases"].obtener_por_id(clase.id)
    assert clase_guardada.cupo_disponible == 0


def test_cu02_reservar_sin_cupo_va_a_lista_de_espera(reserva_service, repos):
    socio_1 = crear_socio()
    socio_2 = crear_socio()
    clase = crear_clase(capacidad=1)  # 1 solo lugar
    for s in (socio_1, socio_2):
        repos["socios"].guardar(s)
    repos["clases"].guardar(clase)

    reserva_service.reservar_clase(socio_1.id, clase.id)
    resultado_2 = reserva_service.reservar_clase(socio_2.id, clase.id)

    assert resultado_2.estado == EstadoReservaDTO.EN_LISTA_ESPERA
    assert resultado_2.posicion_en_espera == 1


def test_cu03_cancelar_reserva_promueve_automaticamente_a_lista_de_espera(reserva_service, repos):
    socio_1 = crear_socio()
    socio_2 = crear_socio()
    clase = crear_clase(capacidad=1)
    for s in (socio_1, socio_2):
        repos["socios"].guardar(s)
    repos["clases"].guardar(clase)

    reserva_service.reservar_clase(socio_1.id, clase.id)
    reserva_service.reservar_clase(socio_2.id, clase.id)  # queda en lista de espera

    resultado_cancelacion = reserva_service.cancelar_reserva(socio_1.id, clase.id)

    assert resultado_cancelacion.exito is True
    assert resultado_cancelacion.socio_promovido_id == socio_2.id

    clase_guardada = repos["clases"].obtener_por_id(clase.id)
    reserva_socio_2 = next(r for r in clase_guardada.reservas if r.socio_id == socio_2.id)
    assert reserva_socio_2.estado.name == "CONFIRMADA"


def test_invariante_capacidad_maxima_nunca_se_excede(reserva_service, repos):
    """Invariante #1 del aggregate ClaseProgramada."""
    clase = crear_clase(capacidad=2)
    repos["clases"].guardar(clase)
    socios = [crear_socio() for _ in range(5)]
    for s in socios:
        repos["socios"].guardar(s)
        reserva_service.reservar_clase(s.id, clase.id)

    clase_guardada = repos["clases"].obtener_por_id(clase.id)
    assert len(clase_guardada.reservas_activas) == 2  # nunca mas de capacidad_maxima
    assert len(clase_guardada.lista_espera) == 3
