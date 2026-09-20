# Partidos de hoy

`TodayEventsService` convierte el día natural del usuario a un intervalo UTC
semiabierto y consulta los eventos ordenados por hora de inicio. La consulta
limita resultados y carga los nombres relacionados con eager loading para evitar
N+1 queries.

La interfaz Telegram solo solicita el caso de uso y renderiza el resumen; no
realiza consultas ni cálculos de fechas directamente.
