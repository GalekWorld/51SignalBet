# Integración de providers

La aplicación consume providers a través de `app.providers.contracts.OddsProvider`.
El resto del sistema recibe modelos normalizados y no conoce nombres de campos ni
endpoints externos.

## Odds API

`OddsApiProvider` implementa el contrato documentado en
`external/odds-api/openapi.yaml`:

- base URL: `https://api.odds-api.net/v1`;
- autenticación: header `X-API-Key`;
- catálogo: `/sports` y `/leagues`;
- eventos: `/events` y `/events/{event_id}`;
- cuotas: `/events/{event_id}/odds/snapshot`.

Las respuestas se validan y se convierten a modelos propios. Las cuotas se
representan con `Decimal`, los timestamps Unix se convierten a UTC y los errores
HTTP se traducen a excepciones de dominio del provider.

Los tests usan `httpx.MockTransport`; CI no realiza llamadas a Internet.
