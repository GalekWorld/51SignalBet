# Administración

Los permisos se resuelven mediante `UserRole`, `Capability` y
`has_capability`; no se dispersan comprobaciones de roles por handlers. Los
cambios de rol pasan por `AdminService` y generan un `AuditLog` inmutable.

Esta fase prepara la capa de administración sin construir todavía un panel web.
