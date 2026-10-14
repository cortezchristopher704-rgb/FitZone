"""Entity Instructor (Etapa 3). Tiene identidad propia pero no es Aggregate Root:
siempre se accede y se modifica a traves de ClaseProgramada o de su propio repositorio
de solo-lectura (IInstructorRepository, Etapa 5)."""
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Instructor:
    nombre: str
    especialidad: str = ""
    id: UUID = field(default_factory=uuid4)

    def asignar_backup(self, instructor_backup: "Instructor") -> None:
        """US-020: reasignacion de instructor de respaldo. La logica de negocio
        real (notificar a los socios inscritos) vive en ClaseProgramada /
        NotificacionService, no aqui; este metodo solo es un marcador de
        intencion para mantener el lenguaje ubicuo del BRD."""
        if instructor_backup.id == self.id:
            raise ValueError("Un instructor no puede ser su propio backup")
