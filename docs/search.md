# Búsqueda

`EventSearchService` busca inicialmente en PostgreSQL por equipos y ligas, sin
introducir un motor externo. Normaliza mayúsculas, espacios y acentos antes de
construir la consulta, limita la respuesta y devuelve `next_offset` cuando hay
más resultados.

La consulta utiliza joins y eager loading para devolver resultados compactos sin
N+1 queries. Se puede reemplazar o ampliar cuando PostgreSQL deje de ser
suficiente, manteniendo el servicio como límite de aplicación.
