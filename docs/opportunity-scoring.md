# Opportunity scoring

El score es una capa de ranking, no una probabilidad ni una garantía. Combina
edge (40%), expected value (35%), cobertura de bookmakers (15%) y frescura de
datos (10%). Cada componente se limita a `[0, 1]` y el resultado final a una
escala interpretable de `0` a `100`.

Los límites son configurables y la salida incluye los componentes para que API,
Telegram y alertas puedan explicar por qué una oportunidad obtuvo su puntuación.
