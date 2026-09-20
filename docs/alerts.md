# Alert Engine

Las reglas de alerta admiten métricas de cuota, expected value, edge y movimiento,
operadores `>=` y `<=`, filtros por dimensiones, cooldown y deduplicación.

`AlertService` separa la evaluación pura de la creación persistente de
`AlertEvent`. La constraint `rule_id + dedup_key` protege contra duplicados entre
workers; las notificaciones se incorporarán en una fase posterior.
