"""
Módulo de configuración de la aplicación.

- Carga las variables desde el archivo .env usando env_loader.
- Convierte los valores a sus tipos correctos dentro de la dataclass AppSettings.
- Expone una instancia global SETTINGS, inmutable, que representa la configuración
  de toda la aplicación.
"""

import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .env_loader import load_env_file

# --------------------------------------------------------------------
# Carga cruda del .env en un diccionario de strings
# --------------------------------------------------------------------

_ENV: Dict[str, str] = load_env_file(".env")


def _get(name: str, cast: Callable[[str], Any]) -> Any:
    """
    Obtiene una variable requerida desde _ENV y la castea.
    Lanza error si no existe o no se puede convertir.
    """
    raw = _ENV.get(name)
    if raw is None:
        raise KeyError(f"Variable requerida '{name}' no está definida en .env")
    try:
        return cast(raw)
    except Exception:
        raise ValueError(f"No se pudo convertir el valor de '{name}' en .env")


def _get_opt(name: str, default: Any, cast: Callable[[str], Any]) -> Any:
    """
    Obtiene una variable opcional desde _ENV, aplicando cast si existe.
    Si no existe, devuelve default.
    """
    raw = _ENV.get(name)
    if raw is None:
        return default
    try:
        return cast(raw)
    except Exception:
        raise ValueError(f"No se pudo convertir el valor de '{name}' en .env")


def _parse_list(raw: str) -> List[str]:
    """
    Convierte una cadena separada por comas en una lista de strings limpios.
    INVENTORY_CLASSES=Item1, Item2, Item3
    """
    return [s.strip() for s in raw.split(",") if s.strip()]


# --------------------------------------------------------------------
# Dataclass principal de configuración
# --------------------------------------------------------------------

@dataclass(frozen=True)
class AppSettings:
    # Rutas y archivos
    SAVEDMODEL_DIR: str
    EXCEL_PATH: str
    IMG_DIR: str

    # Parámetros de cámara / modelo
    INPUT_SIZE: int
    FRAME_W: int
    FRAME_H: int
    CAM_INDEX: int

    THRESHOLD: float
    CONFIRM_FRAMES: int
    NO_OBJECT_CLASS: str

    # Backend de modelo
    MODEL_BACKEND: str           # "local" o "google"
    GCLOUD_CREDENTIALS: str      # ruta al JSON de credenciales de Vision (si se usa)

    # Backend de inventario
    INVENTORY_BACKEND: str       # "excel", "google_sheet" o "multi"
    GSHEET_ID: str
    GSHEET_WORKSHEET: str
    GSHEET_CREDENTIALS: str

    # Clases que cuentan como inventario (por nombre)
    INVENTORY_CLASSES: List[str]


def load_settings() -> AppSettings:
    """
    Construye la configuración de la aplicación a partir del contenido del .env.

    Esta función es el único lugar donde se hace:
    - lectura cruda de variables,
    - conversión de tipo,
    - manejo de valores por defecto.
    """
    return AppSettings(
        # Rutas
        SAVEDMODEL_DIR=_get("SAVEDMODEL_DIR", str),
        EXCEL_PATH=_get("EXCEL_PATH", str),
        IMG_DIR=_get("IMG_DIR", str),

        # Cámara / modelo
        INPUT_SIZE=_get("INPUT_SIZE", int),
        FRAME_W=_get("FRAME_W", int),
        FRAME_H=_get("FRAME_H", int),
        CAM_INDEX=_get("CAM_INDEX", int),

        THRESHOLD=_get("THRESHOLD", float),
        CONFIRM_FRAMES=_get("CONFIRM_FRAMES", int),
        NO_OBJECT_CLASS=_get("NO_OBJECT_CLASS", str),

        # Backend de modelo
        MODEL_BACKEND=_ENV.get("MODEL_BACKEND", "local"),
        GCLOUD_CREDENTIALS=_ENV.get("GCLOUD_CREDENTIALS", ""),

        # Backend de inventario
        INVENTORY_BACKEND=_ENV.get("INVENTORY_BACKEND", "excel"),
        GSHEET_ID=_ENV.get("GSHEET_ID", ""),
        GSHEET_WORKSHEET=_ENV.get("GSHEET_WORKSHEET", "Hoja 1"),
        GSHEET_CREDENTIALS=_ENV.get("GSHEET_CREDENTIALS", ""),

        # Clases de inventario
        INVENTORY_CLASSES=_parse_list(_ENV.get("INVENTORY_CLASSES", "")),
    )


# --------------------------------------------------------------------
# Instancia global única de configuración
# --------------------------------------------------------------------

SETTINGS: AppSettings = load_settings()
