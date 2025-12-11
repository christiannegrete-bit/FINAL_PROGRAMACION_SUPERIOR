"""
Módulo de configuración de la aplicación.

- Carga las variables desde un archivo .env usando EnvLoader.
- Convierte los valores a sus tipos correctos dentro de la dataclass AppSettings.
- Expone una API orientada a objetos mediante SettingsManager (sin variables ni funciones globales ejecutadas al importar).
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .env_loader import EnvLoader


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


class BaseSettingsBuilder:
    """
    Clase base con utilidades para leer y castear valores desde un diccionario
    crudo de configuración (strings).
    """

    def __init__(self, env: Dict[str, str]) -> None:
        self._env = env

    def _get(self, name: str, cast: Callable[[str], Any]) -> Any:
        """
        Obtiene una variable requerida desde self._env y la castea.
        Lanza error si no existe o no se puede convertir.
        """
        raw = self._env.get(name)
        if raw is None:
            raise KeyError(f"Variable requerida '{name}' no está definida en .env")
        try:
            return cast(raw)
        except Exception:
            raise ValueError(f"No se pudo convertir el valor de '{name}' en .env")

    def _get_opt(self, name: str, default: Any, cast: Callable[[str], Any]) -> Any:
        """
        Obtiene una variable opcional desde self._env, aplicando cast si existe.
        Si no existe, devuelve default.
        """
        raw = self._env.get(name)
        if raw is None:
            return default
        try:
            return cast(raw)
        except Exception:
            raise ValueError(f"No se pudo convertir el valor de '{name}' en .env")

    def _parse_list(self, raw: str) -> List[str]:
        """
        Convierte una cadena separada por comas en una lista de strings limpios.
        INVENTORY_CLASSES=Item1, Item2, Item3
        """
        return [s.strip() for s in raw.split(",") if s.strip()]


class EnvSettingsBuilder(BaseSettingsBuilder):
    """
    Builder concreto que hereda los métodos de BaseSettingsBuilder y construye
    un AppSettings a partir de un diccionario cargado desde un .env.
    """

    def build(self) -> AppSettings:
        """Construye la configuración de la aplicación a partir del contenido del .env."""
        return AppSettings(
            # Rutas
            SAVEDMODEL_DIR=self._get("SAVEDMODEL_DIR", str),
            EXCEL_PATH=self._get("EXCEL_PATH", str),
            IMG_DIR=self._get("IMG_DIR", str),

            # Cámara / modelo
            INPUT_SIZE=self._get("INPUT_SIZE", int),
            FRAME_W=self._get("FRAME_W", int),
            FRAME_H=self._get("FRAME_H", int),
            CAM_INDEX=self._get("CAM_INDEX", int),

            THRESHOLD=self._get("THRESHOLD", float),
            CONFIRM_FRAMES=self._get("CONFIRM_FRAMES", int),
            NO_OBJECT_CLASS=self._get("NO_OBJECT_CLASS", str),

            # Backend de modelo
            MODEL_BACKEND=self._env.get("MODEL_BACKEND", "local"),
            GCLOUD_CREDENTIALS=self._env.get("GCLOUD_CREDENTIALS", ""),

            # Backend de inventario
            INVENTORY_BACKEND=self._env.get("INVENTORY_BACKEND", "excel"),
            GSHEET_ID=self._env.get("GSHEET_ID", ""),
            GSHEET_WORKSHEET=self._env.get("GSHEET_WORKSHEET", "Hoja 1"),
            GSHEET_CREDENTIALS=self._env.get("GSHEET_CREDENTIALS", ""),

            # Clases de inventario
            INVENTORY_CLASSES=self._parse_list(
                self._env.get("INVENTORY_CLASSES", "")
            ),
        )


class SettingsManager:
    """
    Punto central de acceso a la configuración de la aplicación.

    - No ejecuta nada automáticamente al importar el módulo.
    - Mantiene una instancia interna de AppSettings encapsulada en un atributo de clase.
    """

    _settings: Optional[AppSettings] = None

    @classmethod
    def load_from_env(cls, env_path: str = ".env") -> AppSettings:
        """
        Carga el archivo .env, construye un AppSettings y lo almacena internamente.

        Debe llamarse explícitamente (por ejemplo, al inicio de main.py).
        """
        raw_env = EnvLoader(env_path).load()
        builder = EnvSettingsBuilder(raw_env)
        settings = builder.build()
        cls._settings = settings
        return settings

    @classmethod
    def get_settings(cls) -> AppSettings:
        """
        Devuelve la configuración ya cargada.

        Lanza error si aún no se ha llamado a load_from_env.
        """
        if cls._settings is None:
            raise RuntimeError(
                "AppSettings no ha sido cargado. Llama primero a "
                "SettingsManager.load_from_env()."
            )
        return cls._settings
