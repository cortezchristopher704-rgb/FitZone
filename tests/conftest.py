from datetime import datetime, timedelta, timezone

import pytest

from src.aplicacion.asistencia_service import AsistenciaService
from src.aplicacion.control_acceso_service import ControlAccesoService
from src.aplicacion.reserva_service import ReservaService
from src.dominio.clase_programada import ClaseProgramada
from src.dominio.instructor import Instructor
from src.dominio.socio import EstadoMembresia, Membresia, Socio
from src.dominio.value_objects import Horario, Plan, Vigencia
from src.infraestructura.repositorios import (
    ClaseProgramadaRepositoryEnMemoria,
    InstructorRepositoryEnMemoria,
    SocioRepositoryEnMemoria,
)
from src.infraestructura.unit_of_work import UnitOfWorkEnMemoria


@pytest.fixture
def repos():
    return {
        "socios": SocioRepositoryEnMemoria(),
        "clases": ClaseProgramadaRepositoryEnMemoria(),
        "instructores": InstructorRepositoryEnMemoria(),
    }


@pytest.fixture
def uow(repos):
    return UnitOfWorkEnMemoria(socios=repos["socios"], clases=repos["clases"])


@pytest.fixture
def reserva_service(uow):
    return ReservaService(uow)


@pytest.fixture
def asistencia_service(uow):
    return AsistenciaService(uow)


@pytest.fixture
def control_acceso_service(repos):
    return ControlAccesoService(repos["socios"])


def crear_socio(plan_tipo: str = "Basico", limite: int = 2, vigente: bool = True) -> Socio:
    ahora = datetime.now(timezone.utc)
    vigencia = Vigencia(
        fecha_inicio=ahora - timedelta(days=30),
        fecha_fin=ahora + timedelta(days=30) if vigente else ahora - timedelta(days=1),
    )
    membresia = Membresia(
        plan=Plan(tipo=plan_tipo, limite_reservas_simultaneas=limite),
        vigencia=vigencia,
        estado=EstadoMembresia.ACTIVA,
    )
    return Socio(nombre="Socio de prueba", contacto="correo@fitzone.mx", membresia=membresia)


def crear_clase(capacidad: int = 1) -> ClaseProgramada:
    instructor = Instructor(nombre="Instructor de prueba")
    horario = Horario(fecha_hora_inicio=datetime.now(timezone.utc) + timedelta(hours=2), duracion_minutos=50)
    return ClaseProgramada(horario=horario, capacidad_maxima=capacidad, instructor=instructor)
