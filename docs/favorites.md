# Favoritos

Los favoritos usan una referencia explícita `favorite_type + target_id` para
soportar deportes, ligas, equipos, eventos y jugadores sin crear columnas
polimórficas ambiguas. La constraint única por usuario hace idempotente añadir el
mismo favorito varias veces.
