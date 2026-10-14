"""
Pruebas de CU-04 y CU-05 -- CU-05 corresponde al Diagrama de secuencia 2
(flujo de excepcion) de la Etapa 8.
"""
from src.dominio.socio import EstadoSocio
from tests.conftest import crear_clase, crear_socio


def test_cu05_tercer_no_show_del_mes_sanciona_al_socio(asistencia_service, repos):
    socio = crear_socio()
    clase = crear_clase()
    repos["socios"].guardar(socio)
    repos["clases"].guardar(clase)

    asistencia_service.procesar_inasistencia(socio.id, clase.id)
    asistencia_service.procesar_inasistencia(socio.id, clase.id)
    resultado_tercero = asistencia_service.procesar_inasistencia(socio.id, clase.id)

    socio_guardado = repos["socios"].obtener_por_id(socio.id)
    assert socio_guardado.estado == EstadoSocio.SANCIONADO
    assert socio_guardado.sancion_hasta is not None
    assert resultado_tercero.mensaje == "SocioBloqueadoPorInasistencia"


def test_cu05_menos_de_tres_no_shows_no_sanciona(asistencia_service, repos):
    socio = crear_socio()
    clase = crear_clase()
    repos["socios"].guardar(socio)
    repos["clases"].guardar(clase)

    resultado = asistencia_service.procesar_inasistencia(socio.id, clase.id)

    socio_guardado = repos["socios"].obtener_por_id(socio.id)
    assert socio_guardado.estado == EstadoSocio.ACTIVO
    assert resultado.mensaje == "InasistenciaRegistrada"


def test_cu04_sancion_por_inasistencia_no_bloquea_acceso_fisico(asistencia_service, control_acceso_service, repos):
    """Regla de negocio N4: el bloqueo de no-shows afecta reservas, NO el
    acceso fisico al gimnasio."""
    socio = crear_socio()
    clase = crear_clase()
    repos["socios"].guardar(socio)
    repos["clases"].guardar(clase)

    for _ in range(3):
        asistencia_service.procesar_inasistencia(socio.id, clase.id)

    resultado_acceso = control_acceso_service.validar_acceso_fisico(socio.id, torniquete_id="T-01")

    assert resultado_acceso.permitido is True


def test_cu04_membresia_vencida_deniega_acceso_fisico(control_acceso_service, repos):
    socio = crear_socio(vigente=False)
    repos["socios"].guardar(socio)

    resultado = control_acceso_service.validar_acceso_fisico(socio.id, torniquete_id="T-01")

    assert resultado.permitido is False
    assert resultado.motivo == "MembresiaVencida"
