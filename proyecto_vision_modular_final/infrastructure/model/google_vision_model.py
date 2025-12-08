from __future__ import annotations

import os
from typing import Sequence, Any, Dict, List

import cv2
import numpy as np
import tensorflow as tf
from google.cloud import vision

from interfaces import IModel


class GoogleVisionModel(IModel):
    """
    Implementación de IModel usando Google Cloud Vision API.

    Comportamiento:
    - Intenta llamar a Vision API.
    - Si hay algún error (billing deshabilitado, servicio desactivado, etc.),
      muestra un WARN UNA vez, marca el modelo como deshabilitado y a partir de
      ahí SIEMPRE devuelve un fallback seguro sin volver a llamar a la API.
    """

    def __init__(self, credentials_path: str, class_names: Sequence[str]) -> None:
        if not os.path.isfile(credentials_path):
            raise FileNotFoundError(
                f"[GoogleVisionModel] No se encontró el archivo de credenciales: {credentials_path}"
            )

        # La librería oficial usa esta variable para localizar las credenciales
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self._client = vision.ImageAnnotatorClient()
        self._class_names: List[str] = list(class_names)

        # Si se produce un error externo (billing, servicio, etc.), ponemos esto en True
        self._disabled = False

    # ----------------- helpers internos -----------------

    def _tensor_to_image_bytes(self, input_tensor: Any) -> bytes:
        """
        Convierte el tensor de entrada (1, H, W, 3) con valores en [0,1]
        a una imagen JPEG en bytes.
        """
        if isinstance(input_tensor, tf.Tensor):
            arr = input_tensor.numpy()
        else:
            arr = np.array(input_tensor)

        # Esperamos batch de 1: (1, H, W, 3)
        if arr.ndim == 4 and arr.shape[0] == 1:
            arr = arr[0]
        # Valores en [0,1] → [0,255] uint8
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)

        # El preprocesador trabaja en RGB, OpenCV usa BGR
        success, buf = cv2.imencode(".jpg", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if not success:
            raise RuntimeError("[GoogleVisionModel] No se pudo codificar la imagen a JPEG")

        return buf.tobytes()

    def _call_api(self, image_bytes: bytes):
        image = vision.Image(content=image_bytes)
        response = self._client.label_detection(image=image)
        if response.error.message:
            raise RuntimeError(
                f"[GoogleVisionModel] Error en Vision API: {response.error.message}"
            )
        return response.label_annotations

    def _labels_to_logits(self, labels) -> np.ndarray:
        """
        Mapea las labels devueltas por Vision API a un vector de logits
        alineado con self._class_names.
        """
        logits = np.zeros((1, len(self._class_names)), dtype=np.float32)
        if not labels:
            if len(self._class_names) > 0:
                logits[0, 0] = 1.0
            return logits

        # índice por nombre de clase (lowercase)
        idx_by_name = {name.lower(): i for i, name in enumerate(self._class_names)}

        any_match = False
        for lbl in labels:
            name = (lbl.description or "").lower()
            if name in idx_by_name:
                i = idx_by_name[name]
                logits[0, i] = max(logits[0, i], float(lbl.score))
                any_match = True

        if not any_match:
            # fallback súper conservador
            logits[0, 0] = 1.0

        return logits

    def _safe_fallback(self) -> Dict[str, np.ndarray]:
        """
        Fallback seguro cuando la API no está disponible:
        por simplicidad, marcamos todo como clase 0 al 100%.
        """
        logits = np.zeros((1, len(self._class_names)), dtype=np.float32)
        if len(self._class_names) > 0:
            logits[0, 0] = 1.0
        return {"logits": logits}

    # ----------------- API pública (contrato IModel) -----------------

    def predict(self, input_tensor: Any) -> Dict[str, np.ndarray]:
        """
        Implementa el mismo contrato que TMSavedModel:
        devuelve un dict con un solo tensor (logits) para que InferenceEngine
        pueda aplicar softmax igual que con el modelo local.
        """

        # Si ya detectamos que la API está caída/deshabilitada, ni lo intentamos
        if self._disabled:
            return self._safe_fallback()

        try:
            image_bytes = self._tensor_to_image_bytes(input_tensor)
            labels = self._call_api(image_bytes)
            logits = self._labels_to_logits(labels)
            return {"logits": logits}
        except Exception as e:
            # Primer fallo: avisamos y deshabilitamos definitivamente este backend
            print(f"[WARN] GoogleVisionModel: fallo la llamada a Vision API, se deshabilita el backend Google. Detalle: {e}")
            self._disabled = True
            return self._safe_fallback()
