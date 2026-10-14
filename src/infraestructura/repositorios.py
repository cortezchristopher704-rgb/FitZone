"""
Interfaces de Repository (Etapa 5) + implementaciones en memoria para
pruebas y para ejecutar este codigo base sin una base de datos real.

Las interfaces hablan en terminos del dominio (ObtenerPorId, Guardar);
ninguna expone SQL ni detalles de un ORM, tal como exige la Etapa 5 y
confirma el ADR-03 ("la aplicacion y el dominio dependen de
abstracciones, no de infraestructura concreta").
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional
from uuid import UUID

from src.dominio.clase_programada import ClaseProgramada
from src.dominio.instructor import Instructor
from src.dominio.socio import Socio


class ISocioRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, id_: UUID) -> Optional[Socio]:
        ...

    @abstractmethod
    def guardar(self, socio: Socio) -> None:
        ...


class IClaseProgramadaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, id_: UUID) -> Optional[ClaseProgramada]:
        ...

    @abstractmethod
    def guardar(self, clase: ClaseProgramada) -> None:
        ...

    @abstractmethod
    def listar_todas(self) -> list[ClaseProgramada]:
        """Necesario para que ReservaService pueda contar cuantas reservas
        activas tiene un socio A TRAVES de todas las clases (regla de
        'limite de reservas simultaneas por plan', US-001/US-013), ya que
        esa informacion no vive dentro de un solo Aggregate ClaseProgramada."""
        ...


class IInstructorRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, id_: UUID) -> Optional[Instructor]:
        ...

    @abstractmethod
    def consultar_disponibles(self) -> list[Instructor]:
        ...


# ---------------------------------------------------------------------
# Implementaciones en memoria (sustituyen a un adaptador real de EF/SQL/
# Mongo). Suficientes como "codigo minimo que represente la arquitectura
# propuesta" (entregable 06) y para que las pruebas corran sin
# dependencias externas.
# ---------------------------------------------------------------------
class SocioRepositoryEnMemoria(ISocioRepository):
    def __init__(self) -> None:
        self._datos: Dict[UUID, Socio] = {}

    def obtener_por_id(self, id_: UUID) -> Optional[Socio]:
        return self._datos.get(id_)

    def guardar(self, socio: Socio) -> None:
        self._datos[socio.id] = socio


class ClaseProgramadaRepositoryEnMemoria(IClaseProgramadaRepository):
    def __init__(self) -> None:
        self._datos: Dict[UUID, ClaseProgramada] = {}

    def obtener_por_id(self, id_: UUID) -> Optional[ClaseProgramada]:
        return self._datos.get(id_)

    def guardar(self, clase: ClaseProgramada) -> None:
        self._datos[clase.id] = clase

    def listar_todas(self) -> list[ClaseProgramada]:
        return list(self._datos.values())


class InstructorRepositoryEnMemoria(IInstructorRepository):
    def __init__(self) -> None:
        self._datos: Dict[UUID, Instructor] = {}

    def obtener_por_id(self, id_: UUID) -> Optional[Instructor]:
        return self._datos.get(id_)

    def consultar_disponibles(self) -> list[Instructor]:
        return list(self._datos.values())

    def guardar(self, instructor: Instructor) -> None:
        self._datos[instructor.id] = instructor
