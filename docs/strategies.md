# Strategy engine

Las estrategias implementan un contrato pequeño (`select`) y reciben únicamente
contexto disponible en el momento de decisión. `ThresholdValueStrategy` es la
primera implementación: filtra por edge y opcionalmente por score.

Cada estrategia tiene `name` y `version` para que backtests y publicaciones
puedan identificar exactamente la lógica usada. No se añaden todavía staking
adaptativo ni modelos predictivos.
