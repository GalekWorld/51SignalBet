# Desarrollo

El proyecto requiere Python 3.12+.

Las dependencias de runtime y desarrollo están declaradas en `pyproject.toml`.
Las variables de entorno se documentan en `.env.example`; ningún secreto debe
entrar en Git.

Cada fase debe incluir sus tests, checks de Ruff y mypy relevantes, y actualizar
la documentación solo cuando cambie una decisión o el flujo de desarrollo.
