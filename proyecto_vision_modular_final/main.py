"""
La aplicación principal que integra todos los módulos para el sistema de inventario con visión 
por computadora.

1. Carga la configuración desde el módulo bootstrap (load_app_settings), que a su vez usa 
   AppSettings y validate_settings para asegurar rutas y parámetros correctos.

2. Inicializa la cámara, el modelo, el preprocesador, el repositorio de inventario 
   (Excel, Google Sheets o ambos usando MultiInventoryRepo) y la UI de detalle.

3. Construye el motor de inferencia y el controlador de la aplicación mediante inyección de 
   dependencias, lo que garantiza bajo acoplamiento y fácil extensibilidad del sistema.

4. Arranca el bucle principal de la aplicación, manejando errores globales para evitar 
   fallos silenciosos y garantizando una ejecución robusta.
"""

from tkinter import Tk

from config.bootstrap import load_app_settings

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


def main() -> None:
    try:
        # --- Cargar configuración validada ---
        settings = load_app_settings()

        # --- UI base ---
        root = Tk()
        root.withdraw()

        # --- Cámara ---
        camera = OpenCVCamera(
            index=settings.CAM_INDEX,
            width=settings.FRAME_W,
            height=settings.FRAME_H,
        )

        # --- Preprocesador ---
        preprocessor = TMPreprocessor(settings.INPUT_SIZE)

        # --- Backend de inventario ---
        if settings.INVENTORY_BACKEND == "excel":
            repo = ExcelInventoryRepo(settings.EXCEL_PATH)

        elif settings.INVENTORY_BACKEND == "google_sheet":
            repo = GoogleSheetInventoryRepo(
                spreadsheet_id=settings.GSHEET_ID,
                worksheet_name=settings.GSHEET_WORKSHEET,
                credentials_path=settings.GSHEET_CREDENTIALS,
            )

        elif settings.INVENTORY_BACKEND == "multi":
            repo = MultiInventoryRepo([
                ExcelInventoryRepo(settings.EXCEL_PATH),
                GoogleSheetInventoryRepo(
                    spreadsheet_id=settings.GSHEET_ID,
                    worksheet_name=settings.GSHEET_WORKSHEET,
                    credentials_path=settings.GSHEET_CREDENTIALS,
                )
            ])

        else:
            raise ValueError(
                f"[main] INVENTORY_BACKEND inválido: {settings.INVENTORY_BACKEND!r}. "
                "Usa 'excel', 'google_sheet' o 'multi'."
            )

        # --- UI de Detalle ---
        detail_ui = TkDetailUI(root=root, repo=repo)

        # --- Clases del modelo ---
        class_names = InferenceEngine.load_labels(settings.SAVEDMODEL_DIR)

        # --- Backend del modelo ---
        if settings.MODEL_BACKEND == "local":
            model = TMSavedModel(settings.SAVEDMODEL_DIR)

        elif settings.MODEL_BACKEND == "google":
            model = GoogleVisionModel(
                credentials_path=settings.GCLOUD_CREDENTIALS,
                class_names=class_names,
            )

        else:
            raise ValueError(
                f"[main] MODEL_BACKEND inválido: {settings.MODEL_BACKEND!r}. "
                "Usa 'local' o 'google'."
            )

        # --- Motor de inferencia ---
        engine = InferenceEngine(
            preprocessor=preprocessor,
            model=model,
            class_names=class_names,
        )

        # Las primeras N clases se consideran válidas para inventario
        valid_classes = set(class_names[:4])

        # --- Controlador principal ---
        controller = AppController(
            camera=camera,
            engine=engine,
            ui=detail_ui,
            class_names=class_names,
            valid_classes=valid_classes,
            no_object_class=settings.NO_OBJECT_CLASS,
            threshold=settings.THRESHOLD,
            confirm_frames=settings.CONFIRM_FRAMES,
        )

        controller.run(root)

    except Exception as e:
        print(f"[ERROR] Ha ocurrido un error en la aplicación principal: {e}")


if __name__ == "__main__":
    main()
