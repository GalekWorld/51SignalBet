# Sports data provider

La Fase 33 separa el contrato de datos deportivos del contrato de cuotas. En
particular, `SportsDataProvider` permite incorporar resultados y metadatos sin
acoplarlos a `OddsProvider`.

La implementación incluida es de fixtures para pruebas y desarrollo. Los
resultados reales deberán incorporarse mediante un adapter documentado y
validado, sin inventar endpoints ni mezclar sus modelos con el dominio interno.
