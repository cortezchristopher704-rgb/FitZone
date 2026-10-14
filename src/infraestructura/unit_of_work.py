"""
Unit of Work (Etapa 5 / ADR-02).

Garantiza que "liberar lugar + promover de la lista de espera" (CU-03)
se confirme o se revierta como una sola operacion atomica. En esta
version en memoria, commit() simplemente guarda el estado final de
los aggregates tocados; en una infraestructura real (EF Core, SQLAlchemy,
una transaccion de base de datos) commit()/rollback() envolverian una
transaccion real.
"""
from __future__ import annotations

from typing import List, Protocol

from src.dominio.clase_programada import ClaseProgramada
from src.dominio.socio import Socio
from src.infraestructura.repositorios import (
    IClaseProgramadaRepository,
    ISocioRepository,
)


class IUnitOfWork(Protocol):
    socios: ISocioRepository
    clases: IClaseProgramadaRepository

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def registrar_cambio(self, aggregate: ClaseProgramada | Socio) -> None: ...


class UnitOfWorkEnMemoria:
    """Implementacion simple: acumula los aggregates modificados durante
    el caso de uso y los persiste todos juntos en commit(), o los
    descarta en rollback() (no quedan guardados)."""

    def __init__(self, socios: ISocioRepository, clases: IClaseProgramadaRepository) -> None:
        self.socios = socios
        self.clases = clases
        self._pendientes: List[ClaseProgramada | Socio] = []

    def registrar_cambio(self, aggregate: ClaseProgramada | Socio) -> None:
        if aggregate not in self._pendientes:
            self._pendientes.append(aggregate)

    def commit(self) -> None:
        for aggregate in self._pendientes:
            if isinstance(aggregate, ClaseProgramada):
                self.clases.guardar(aggregate)
                aggregate.limpiar_eventos()
            elif isinstance(aggregate, Socio):
                self.socios.guardar(aggregate)
                aggregate.limpiar_eventos()
        self._pendientes.clear()

    def rollback(self) -> None:
        # En memoria: como aun no se llamo a guardar(), basta con
        # descartar la lista de pendientes; el estado persistido
        # (el que ya estaba en el repositorio) nunca se toco.
        self._pendientes.clear()

    def __enter__(self) -> "UnitOfWorkEnMemoria":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        # si no hubo excepcion, quien use el UoW decide cuando hacer commit()
