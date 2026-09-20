# Feature engineering

`FeaturePipeline` genera features con versión y cutoff temporal explícito. Las
observaciones posteriores a `as_of` se rechazan para evitar lookahead. La primera
versión incluye probabilidad implícita, horas hasta el inicio, movimiento desde
apertura, cobertura de bookmakers y frescura.

El pipeline no entrena modelos ni persiste predicciones; prepara entradas
reproducibles para fases posteriores.
