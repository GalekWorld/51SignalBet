# Segundo provider

`FixtureOddsProvider` es una segunda implementación del contrato
`OddsProvider`, basada en fixtures inyectadas. Sirve para desarrollo, contract
tests y validar que los servicios no dependen de `OddsApiProvider`.

No representa un feed de producción ni inventa endpoints externos. La integración
de un segundo proveedor real debe añadir su adapter documentado y sus fixtures
contractuales detrás del mismo contrato.
