# Backtesting

`BacktestEngine` es un módulo propio separado de la ingesta y de los providers.
Rechaza inputs con lookahead (`information_at > placed_at` o resultados conocidos
antes de la colocación), ordena temporalmente las bets y simula bankroll,
drawdown, ROI y yield.

Walk-forward, estrategias y staking avanzado permanecen fuera de esta fase.
