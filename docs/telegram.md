# Telegram core

La identidad de usuario se vincula mediante `telegram_user_id` en la tabla
`users`. Cada `/start` crea o actualiza el usuario y registra `last_active_at`.

Los handlers solo coordinan la interacción: delegan el registro a
`UserService` y renderizan el menú. La lógica de negocio y el acceso a base de
datos permanecen fuera de Telegram.

La instancia de `Bot` y el `Dispatcher` se construyen mediante factory y no
inician polling al importar módulos. El token se obtiene de configuración, nunca
se hardcodea.
