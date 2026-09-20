# Movimiento de líneas

`LineMovementService` trabaja con observaciones históricas ya normalizadas y
calcula apertura, cuota actual, máximo, mínimo, movimiento absoluto, movimiento
porcentual, velocidad por hora y movimiento por bookmaker.

El análisis siempre ordena por timestamp y permite delimitar explícitamente una
ventana temporal. Los outliers se detectan de forma robusta usando desviación
absoluta mediana entre las cuotas actuales por bookmaker.
