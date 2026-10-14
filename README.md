# FitZone — Diseño arquitectural del sistema

## Descripción
FitZone es un sistema orientado a la gestión de reservas de clases, control de capacidad, listas de espera, validación de acceso físico y aplicación de sanciones por inasistencias.

Este documento resume las decisiones arquitectónicas planteadas en la Actividad 3, correspondiente a la materia **Componentes de Lógica de Negocio**.

## Funcionalidades principales
- **Reservar una clase:** permite a los socios reservar clases en línea.
- **Gestionar lista de espera:** cuando una clase está llena, los socios pueden quedar en espera.
- **Cancelar una reserva:** al cancelar con anticipación, se libera el lugar y se asigna a la siguiente persona en la lista de espera, respetando el orden FIFO.
- **Validar acceso físico:** verifica la vigencia de la membresía antes de permitir el acceso.
- **Aplicar sanciones por inasistencia:** registra las inasistencias y aplica el bloqueo de reservas cuando se alcanza el límite establecido.

## Diseño arquitectónico
La arquitectura utiliza el patrón **Domain Model** como enfoque principal para encapsular las reglas de negocio dentro del dominio.

### Componentes principales
- **Entidades:** `Socio`, `Membresía`, `ClaseProgramada`, `Instructor` y `Reserva`.
- **Objetos de valor:** `Vigencia`, `Horario`, `CapacidadMaxima`, `CupoDisponible` y `Plan`.
- **Servicios de aplicación:** `ReservaService`, `ControlAccesoService`, `AsistenciaService` y `DropInService`.
- **Servicio de notificaciones:** `NotificacionService`, separado para mantener una única responsabilidad.
- **Repositorios:** `ISocioRepository`, `IClaseProgramadaRepository` e `IInstructorRepository`.
- **Unidad de trabajo:** ayuda a mantener la consistencia de operaciones relacionadas, como cancelar una reserva y promover al siguiente socio de la lista de espera.
- **Consultas CQRS:** se contempla su uso básico para consultas de disponibilidad de clases y estado del socio.

## Reglas de negocio relevantes
- La membresía debe estar vigente y el plan debe permitir la reserva solicitada.
- No se puede superar la capacidad máxima de una clase.
- La lista de espera se atiende en orden FIFO.
- Una cancelación anticipada libera el lugar para la siguiente persona en espera.
- Si la membresía está vencida, se deniega el acceso físico y se cancelan las reservas futuras activas, de acuerdo con las reglas del sistema.
- Al acumular **3 inasistencias en un mes**, se bloquean las reservas durante **7 días**. El acceso físico sigue permitido.
- La inscripción extraordinaria (*Drop-In*) requiere pago y no modifica la membresía base.

## Eventos de dominio considerados
- `ReservaConfirmada`
- `LugarLiberadoEnClase`
- `ClaseCanceladaPorInstructor`
- `SocioBloqueadoPorInasistencia`
- `AccesoFisicoDenegado`
- `MembresiaVencida`

## Pruebas
El reporte de la actividad indica que se ejecutaron **9 pruebas automatizadas y las 9 fueron aprobadas**.

## Equipo de trabajo
- Christopher Cortez Garcia
- Oscar Elias Vera Moreno
- Christofer Aaron Torres Puga

**Asignatura:** Componentes de Lógica de Negocio  
**Actividad:** Diseño arquitectural del sistema FitZone (Unidad 3)  
**Docente:** Miguel Ángel Gómez Marroquín  
**Fecha del reporte:** 17/10/2026
