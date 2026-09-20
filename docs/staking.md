# Staking engine

Se soportan flat stake, fixed units, porcentaje de bankroll y fractional Kelly.
Todas las políticas tienen límites opcionales y nunca aumentan el stake para
recuperar pérdidas. No se implementa martingala.

Kelly requiere una probabilidad explícita; si el edge es negativo, el stake
calculado es cero.
