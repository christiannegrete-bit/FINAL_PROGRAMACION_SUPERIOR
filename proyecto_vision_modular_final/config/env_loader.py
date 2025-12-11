"""
Módulo para cargar variables de entorno desde un archivo .env sin dependencias externas.

Se usan dos clases:

- BaseFileLoader: encapsula la lógica común de manejo de rutas y verificación de existencia.
- EnvLoader: hereda de BaseFileLoader y añade la lógica específica para archivos .env.
"""

import os
from typing import Dict


class BaseFileLoader:
    """Clase base para loaders de archivos."""

    def __init__(self, path: str) -> None:
        self._path = path

    def _ensure_exists(self) -> None:
        """Verifica que el archivo exista; lanza error si no."""
        if not os.path.exists(self._path):
            raise FileNotFoundError(
                f"No se encontró el archivo requerido en {os.path.abspath(self._path)}"
            )

    @property
    def path(self) -> str:
        """Ruta del archivo que se está manejando."""
        return self._path


class EnvLoader(BaseFileLoader):
    """Loader específico para archivos .env con formato KEY=VALUE."""

    def load(self) -> Dict[str, str]:
        """Carga archivo .env KEY=VALUE sin dependencias externas."""
        self._ensure_exists()
        env: Dict[str, str] = {}

        with open(self._path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                # Soporta comentarios al final de la línea
                value = value.split("#", 1)[0].strip()
                env[key.strip()] = value

        return env
