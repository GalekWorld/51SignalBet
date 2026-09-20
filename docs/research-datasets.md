# Historical research datasets

`ResearchDatasetBuilder` crea datasets reproducibles desde observaciones
históricas. Filtra por ventana temporal, excluye observaciones posteriores a
`generated_at`, puede exigir resultado conocido y ordena de forma determinista.

La exportación CSV conserva timestamps timezone-aware y cuotas como strings
decimales. El dataset incluye una versión explícita para reproducir experimentos.
