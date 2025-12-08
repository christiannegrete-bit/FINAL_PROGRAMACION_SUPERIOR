"""
Módulo para inicializar y validar la configuración de la aplicación.
Proporciona la función load_app_settings que carga y valida las configuraciones
antes de iniciar la aplicación.
"""

# config/bootstrap.py
import os
from .settings import AppSettings, load_settings

def validate_settings(settings: AppSettings) -> None:
    """Valida rutas y parámetros críticos antes de iniciar la app."""

    # Modelo local
    if not os.path.isdir(os.path.dirname(settings.SAVEDMODEL_DIR)):
        raise FileNotFoundError(
            f"SAVEDMODEL_DIR inválido: {settings.SAVEDMODEL_DIR}"
        )

    # Imágenes
    if not os.path.isdir(settings.IMG_DIR):
        raise FileNotFoundError(
            f"IMG_DIR inválido: {settings.IMG_DIR}"
        )

    # Excel
    if settings.INVENTORY_BACKEND in ("excel", "multi"):
        excel_dir = os.path.dirname(settings.EXCEL_PATH)
        if not os.path.isdir(excel_dir):
            raise FileNotFoundError(
                f"EXCEL_PATH inválido: {settings.EXCEL_PATH}"
            )

    # Google Sheets
    if settings.INVENTORY_BACKEND in ("google_sheet", "multi"):
        if not settings.GSHEET_ID:
            raise ValueError(
                "GSHEET_ID es obligatorio para INVENTORY_BACKEND=google_sheet o multi"
            )
        if not os.path.isfile(settings.GSHEET_CREDENTIALS):
            raise FileNotFoundError(
                f"GSHEET_CREDENTIALS inválido: {settings.GSHEET_CREDENTIALS}"
            )

    # Modelo Google Vision (si lo usas)
    if settings.MODEL_BACKEND == "google":
        if not settings.GCLOUD_CREDENTIALS:
            raise ValueError("GCLOUD_CREDENTIALS es obligatorio para MODEL_BACKEND=google")
        if not os.path.isfile(settings.GCLOUD_CREDENTIALS):
            raise FileNotFoundError(
                f"GCLOUD_CREDENTIALS inválido: {settings.GCLOUD_CREDENTIALS}"
            )


def load_app_settings() -> AppSettings:
    """Carga y valida settings; devuelve un AppSettings listo para usar."""
    settings = load_settings()
    validate_settings(settings)
    return settings
