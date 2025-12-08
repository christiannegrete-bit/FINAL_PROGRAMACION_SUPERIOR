# config/env_loader.py
"""
Módulo para cargar variables de entorno desde un archivo .env sin dependencias externas.
Proporciona la función load_env_file que lee un archivo .env simple con formato KEY=VALUE
y devuelve un diccionario con las variables cargadas.
"""
# config/env_loader.py
import os
from typing import Dict

def load_env_file(path: str = ".env") -> Dict[str, str]:
    """Carga archivo .env KEY=VALUE sin dependencias externas."""
    env: Dict[str, str] = {}
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el archivo .env en {os.path.abspath(path)}"
        )

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.split("#", 1)[0].strip()
            env[key.strip()] = value

    return env
