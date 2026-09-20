# Free/Premium

La autorización de producto se resuelve mediante `SubscriptionPlan`,
`Entitlement` y `EntitlementService`. Las interfaces no comprueban
`user.is_premium` directamente.

Esta fase prepara planes FREE, PREMIUM y ADMIN; no implementa pagos ni webhooks.
Una suscripción vencida vuelve a comportarse como FREE.
