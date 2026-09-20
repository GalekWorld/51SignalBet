# Arquitectura inicial

El proyecto empieza como un monolito modular para evitar complejidad prematura.
La dirección de dependencias prevista es:

```text
providers -> services -> repositories -> database
                         ^
                    API / Bot / Jobs
```

La ingesta de eventos usa el provider normalizado y un servicio de aplicación;
los handlers futuros no acceden directamente a SQL ni a la API externa.

## Límites

- `app/core`: configuración y preocupaciones transversales.
- `app/api`: transporte HTTP y schemas/endpoints futuros.
- `app/domain`: reglas y entidades de negocio futuras.
- `app/services`: casos de uso futuros.
- `app/providers`: adapters de servicios externos futuros.
- `app/repositories`: persistencia futura.
- `tests`: pruebas automatizadas separadas del código de producción.
