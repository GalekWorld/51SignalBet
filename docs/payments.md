# Payments

La Fase 26 solo prepara el límite de integración: `PaymentProvider`,
`PaymentWebhook`, `PaymentService` y un historial idempotente de webhooks.

No se ha conectado ningún proveedor, no se crean cobros y ningún webhook cambia
entitlements automáticamente. La activación de planes deberá validarse en una
fase posterior con una política explícita por proveedor.
