# Data quality

`DataQualityService` detecta cuotas stale, retrasos del provider, anomalías de
timestamps, mercados incompletos, cuotas inválidas, conflictos de mapping y
resultados ausentes.

Cada issue tiene severidad `reject` o `degraded`. Las oportunidades solo deben
publicarse cuando no existe ningún issue `reject`; los issues degradados quedan
disponibles para explicar la calidad de la señal.
