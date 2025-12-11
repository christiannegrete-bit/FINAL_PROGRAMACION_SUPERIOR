"""
Aplicación principal que integra todos los módulos para el sistema de inventario
con visión por computadora.

Flujo general:

1. Carga la configuración desde el archivo .env usando SettingsManager y valida
   las rutas/parámetros críticos con AppSettingsValidator.

2. Inicializa:
   - Cámara (OpenCVCamera)
   - Preprocesador (TMPreprocessor)
   - Modelo IA (TMSavedModel o GoogleVisionModel)
   - Repositorio de inventario (Excel, Google Sheets o MultiInventoryRepo)
   - Interfaz gráfica de detalle (TkDetailUI)

3. Construye el motor de inferencia (InferenceEngine) y el controlador principal
   (AppController) mediante inyección de dependencias.

4. Arranca el bucle principal de la aplicación, manejando errores globales para
   evitar fallos silenciosos.
"""

from tkinter import Tk

from config.settings import SettingsManager
from config.bootstrap import AppSettingsValidator
from config.assets import DefaultAssetRegistry

from infrastructure.camera.opencv_camera import OpenCVCamera
from infrastructure.model.Tm_saved_model import TMSavedModel
from infrastructure.model.google_vision_model import GoogleVisionModel

from infrastructure.repo.excel_inventory_repo import ExcelInventoryRepo
from infrastructure.repo.google_sheet_inventory_repo import GoogleSheetInventoryRepo
from infrastructure.repo.multi_inventory_repo import MultiInventoryRepo

from core.inference.inference_engine import InferenceEngine
from core.preprocessing.Tm_preprocessor import TMPreprocessor

from ui.tk_detail_ui import TkDetailUI
from app.controller import AppController


class Application:
    """
    Clase principal que orquesta la configuración, inicialización de dependencias
    y ejecución del controlador.
    """

    def __init__(self, env_path: str = ".env") -> None:
        # 1) Cargar y validar configuración
        settings = SettingsManager.load_from_env(env_path)
        AppSettingsValidator.validate(settings)
        self._settings = settings

        # 2) Inicializar UI base
        root = Tk()
        root.withdraw()
        self._root = root

        # 3) Inicializar cámara
        self._camera = OpenCVCamera(
            index=self._settings.CAM_INDEX,
            width=self._settings.FRAME_W,
            height=self._settings.FRAME_H,
        )
        # Si tu controlador NO llama a open(), lo hacemos aquí:
        self._camera.open()

        # 4) Inicializar preprocesador
        self._preprocessor = TMPreprocessor(self._settings.INPUT_SIZE)

        # 5) Inicializar repositorio de inventario
        self._repo = self._build_inventory_repo()

        # 6) Inicializar registro de assets (para imágenes y datasheets)
        self._asset_registry = DefaultAssetRegistry(
            img_dir=self._settings.IMG_DIR
        )

        # 7) Inicializar UI de detalle
        self._detail_ui = TkDetailUI(
            root=self._root,
            repo=self._repo,
            asset_registry=self._asset_registry,
        )

        # 8) Cargar etiquetas del modelo
        self._class_names = InferenceEngine.load_labels(
            self._settings.SAVEDMODEL_DIR
        )

        # 9) Inicializar backend de modelo
        self._model = self._build_model_backend()

        # 10) Motor de inferencia
        self._engine = InferenceEngine(
            preprocessor=self._preprocessor,
            model=self._model,
            class_names=self._class_names,
        )

        # 11) Clases válidas para inventario (primeras N)
        self._valid_classes = set(self._class_names[:4])

        # 12) Controlador principal
        self._controller = AppController(
            camera=self._camera,
            engine=self._engine,
            ui=self._detail_ui,
            class_names=self._class_names,
            valid_classes=self._valid_classes,
            no_object_class=self._settings.NO_OBJECT_CLASS,
            threshold=self._settings.THRESHOLD,
            confirm_frames=self._settings.CONFIRM_FRAMES,
        )

    # ------------------------------------------------------------------
    # Helpers para construir dependencias
    # ------------------------------------------------------------------

    def _build_inventory_repo(self):
        """Crea el repositorio de inventario apropiado según la configuración."""
        backend = self._settings.INVENTORY_BACKEND

        if backend == "excel":
            return ExcelInventoryRepo(self._settings.EXCEL_PATH)

        if backend == "google_sheet":
            return GoogleSheetInventoryRepo(
                spreadsheet_id=self._settings.GSHEET_ID,
                worksheet_name=self._settings.GSHEET_WORKSHEET,
                credentials_path=self._settings.GSHEET_CREDENTIALS,
            )

        if backend == "multi":
            return MultiInventoryRepo([
                ExcelInventoryRepo(self._settings.EXCEL_PATH),
                GoogleSheetInventoryRepo(
                    spreadsheet_id=self._settings.GSHEET_ID,
                    worksheet_name=self._settings.GSHEET_WORKSHEET,
                    credentials_path=self._settings.GSHEET_CREDENTIALS,
                ),
            ])

        raise ValueError(
            f"[main] INVENTORY_BACKEND inválido: {backend!r}. "
            "Usa 'excel', 'google_sheet' o 'multi'."
        )

    def _build_model_backend(self):
        """Crea el backend de modelo IA según la configuración."""
        backend = self._settings.MODEL_BACKEND

        if backend == "local":
            return TMSavedModel(self._settings.SAVEDMODEL_DIR)

        if backend == "google":
            return GoogleVisionModel(
                credentials_path=self._settings.GCLOUD_CREDENTIALS,
                class_names=self._class_names,
            )

        raise ValueError(
            f"[main] MODEL_BACKEND inválido: {backend!r}. Usa 'local' o 'google'."
        )

    # ------------------------------------------------------------------
    # Ejecución
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Ejecuta el bucle principal de la aplicación."""
        self._controller.run(self._root)


def main() -> None:
    try:
        app = Application(env_path=".env")
        app.run()
    except Exception as e:
        print(f"[ERROR] Ha ocurrido un error en la aplicación principal: {e}")


if __name__ == "__main__":
    main()
