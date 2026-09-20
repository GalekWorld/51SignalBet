# Ficha del evento

`EventDetailService` carga un evento y sus relaciones principales con eager
loading: deporte, liga y equipos. Devuelve un DTO propio y convierte la hora UTC
a la zona horaria del usuario.

La interfaz Telegram valida el callback, llama al servicio y renderiza el
resultado. Los errores de evento inexistente se convierten en un mensaje simple,
sin exponer SQL ni tracebacks.
