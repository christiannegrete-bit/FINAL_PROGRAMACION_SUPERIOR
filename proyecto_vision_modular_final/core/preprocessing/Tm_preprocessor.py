'''
TMPreprocessor es el módulo que toma la imagen cruda de la cámara y la convierte en un tensor listo
para la IA.
    1.- Primero cambia de BGR a RGB, luego escala la imagen al tamaño adecuado, la normaliza en el
      rango 0–1 y finalmente agrega la dimensión batch.

El resultado es un tensor perfectamente compatible con el modelo TensorFlow para ejecutar la inferencia.
'''
import cv2
import numpy as np
from interfaces import IPreprocessor


class TMPreprocessor(IPreprocessor):
    def __init__(self, input_size: int) -> None:
        self._size = input_size

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self._size, self._size), interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 255.0
        return np.expand_dims(img, axis=0)
