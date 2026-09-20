# Jobs y workers

Los jobs se ejecutan como funciones async reutilizables mediante `run_job`. El
runner aplica retries limitados solo a errores transitorios y admite un lock
distribuido Redis para impedir ejecuciones concurrentes del mismo job.

Jobs disponibles:

- `SyncSportsJob`
- `SyncLeaguesJob`
- `SyncEventsJob`
- `SyncOddsJob`

La elección del scheduler externo queda pospuesta hasta conocer la frecuencia y
el número real de workers. El job runner no introduce Celery ni infraestructura
adicional prematuramente.
