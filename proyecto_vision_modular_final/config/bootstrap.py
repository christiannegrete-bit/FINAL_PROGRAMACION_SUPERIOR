"""
Módulo para inicializar y validar la configuración de la aplicación.

Se usan clases:

- BaseSettingsValidator: métodos reutilizables para validar rutas y archivos.
- AppSettingsValidator: hereda de BaseSettingsValidator y valida específicamente AppSettings.
"""

import os
from .settings import AppSettings


class BaseSettingsValidator:
    """Validador base con métodos reutilizables para verificar rutas y archivos."""

    @staticmethod
    def _ensure_directory(path: str, label: str) -> None:
        if not os.path.isdir(path):
            raise FileNotFoundError(f"{label} inválido: {path}")

    @staticmethod
    def _ensure_directory_from_file(path: str, label: str) -> None:
        directory = os.path.dirname(path)
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"{label} inválido: {path}")

    @staticmethod
    def _ensure_file(path: str, label: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{label} inválido: {path}")


class AppSettingsValidator(BaseSettingsValidator):
    """Validador concreto para AppSettings, reusa los métodos de la clase base."""

    @classmethod
    def validate(cls, settings: AppSettings) -> None:
        """Valida rutas y parámetros críticos antes de iniciar la app."""

        # Modelo local
        cls._ensure_directory_from_file(settings.SAVEDMODEL_DIR, "SAVEDMODEL_DIR")

        # Imágenes
        cls._ensure_directory(settings.IMG_DIR, "IMG_DIR")

        # Excel
        if settings.INVENTORY_BACKEND in ("excel", "multi"):
            cls._ensure_directory_from_file(settings.EXCEL_PATH, "EXCEL_PATH")

        # Google Sheets
        if settings.INVENTORY_BACKEND in ("google_sheet", "multi"):
            if not settings.GSHEET_ID:
                raise ValueError(
                    "GSHEET_ID es obligatorio para INVENTORY_BACKEND=google_sheet o multi"
                )
            cls._ensure_file(settings.GSHEET_CREDENTIALS, "GSHEET_CREDENTIALS")

        # Modelo Google Vision (si se usa)
        if settings.MODEL_BACKEND == "google":
            if not settings.GCLOUD_CREDENTIALS:
                raise ValueError(
                    "GCLOUD_CREDENTIALS es obligatorio para MODEL_BACKEND=google"
                )
            cls._ensure_file(settings.GCLOUD_CREDENTIALS, "GCLOUD_CREDENTIALS")
