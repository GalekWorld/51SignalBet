# Calibration

`BinnedCalibrator` ajusta probabilidades mediante tasas empíricas por bins. Si
un bin no tiene observaciones conserva la probabilidad original. La calibración
se mantiene separada del modelo y debe entrenarse únicamente con datos
históricos permitidos por el protocolo de evaluación.
