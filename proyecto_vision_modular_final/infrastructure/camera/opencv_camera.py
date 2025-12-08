'''
OpenCVCamera es la capa de acceso a la cámara.
    1.-Con __init__ configuro qué cámara y qué resolución usar.
    2.-Con open() la inicializo validando que realmente se abra.
    3.-Con read() capturo cada frame y manejo los errores de lectura.
    4.-Con release() libero el dispositivo al final para no dejar la cámara tomada por el programa.
'''
import cv2
import numpy as np

from interfaces import ICamera

class OpenCVCamera(ICamera):
    def __init__(self, index: int, width: int, height: int) -> None:
        self._index = index
        self._width = width
        self._height = height
        self._cap = None

    def open(self) -> None:
        try:
            self._cap = cv2.VideoCapture(self._index, cv2.CAP_DSHOW)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            if not self._cap.isOpened():
                print("[ERROR] Ha ocurrido un error con la cámara: no se pudo abrir.")
                raise RuntimeError("No se pudo abrir la cámara")
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al inicializar la cámara: {e}")
            raise

    def read(self) -> np.ndarray:
        if self._cap is None:
            print("[ERROR] Ha ocurrido un error con la cámara: no está inicializada.")
            raise RuntimeError("Cámara no inicializada")
        ok, frame = self._cap.read()
        if not ok:
            print("[ERROR] Ha ocurrido un error al leer un frame de la cámara.")
            raise RuntimeError("No se pudo leer frame de la cámara")
        return frame

    def release(self) -> None:
        try:
            if self._cap is not None:
                self._cap.release()
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al liberar la cámara: {e}")
            raise
