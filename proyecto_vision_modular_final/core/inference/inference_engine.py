"""
load_labels carga la lista de clases desde el modelo para saber qué nombre corresponde a cada índice.
    1.-InferenceEngine es el motor de predicción: preprocesa la imagen, ejecuta el modelo, convierte 
    los logits en probabilidades y devuelve la etiqueta final con su confianza.
    
Si algo falla en la inferencia, el sistema corta y reporta el error para evitar decisiones incorrectas.
"""
import os
from typing import List, Tuple

import numpy as np
import tensorflow as tf

from interfaces import IPreprocessor, IModel


class InferenceEngine:
    def __init__(self,preprocessor: IPreprocessor,model: IModel,
        class_names: List[str],) -> None:
        self._preprocessor = preprocessor
        self._model = model
        self._class_names = class_names
    
    def load_labels(model_dir: str) -> List[str]:
        """Carga labels desde assets/labels.txt o labels.txt.

        Si falla, devuelve un conjunto por defecto.
        """
        candidates = [
            os.path.join(model_dir, "assets", "labels.txt"),
            os.path.join(model_dir, "labels.txt"),
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        labels = [ln.strip() for ln in f if ln.strip()]
                    if labels:
                        return labels
                except Exception as e:
                    print(f"[ERROR] Ha ocurrido un error al leer labels desde {p}: {e}")
                    raise
        print("[ERROR] No se encontraron labels.txt válidos, usando etiquetas por defecto.")
        return ["Modulo Rele 2", "7404", "Diodo Zener", "7805", "No hay nada"]

    def predict(self, frame) -> Tuple[str, float, np.ndarray]:
        """Devuelve (label, confianza, vector_de_probabilidades)."""
        try:
            img = self._preprocessor.preprocess(frame)
            outputs = self._model.predict(tf.constant(img))
            first_key = list(outputs.keys())[0]
            logits = outputs[first_key]
            probs = tf.nn.softmax(logits, axis=-1).numpy()[0]
            idx = int(np.argmax(probs))
            label = self._class_names[idx]
            conf = float(probs[idx])
            return label, conf, probs
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error durante la inferencia: {e}")
            raise
