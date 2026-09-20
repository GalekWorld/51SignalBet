# Value Engine

`ValueEngine` recibe cuotas normalizadas, probabilidad fair y opcionalmente
probabilidad de modelo. El modelo se utiliza para calcular edge y expected value
cuando existe, pero la probabilidad fair se conserva siempre en la salida.

El motor no ejecuta apuestas, no envía mensajes y no persiste resultados. Devuelve
`ValueOpportunity` solamente cuando las reglas configurables se cumplen.

Fórmulas:

- `edge = p - (1 / odds)`;
- `expected_value = p * (odds - 1) - (1 - p)`.
