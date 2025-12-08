'''
Test de integración del motor de inferencia con preprocesador y modelo falsos.
    1.-FakePreprocessor simula el preprocesamiento devolviendo un tensor fijo.
    2.-FakeModel simula el modelo devolviendo logits fijos que corresponden a una clase conocida.
    3.-test_inference_works valida que InferenceEngine use ambos para devolver la etiqueta y confianza
      correctas según los logits simulados.
'''

import numpy as np
from core.inference.inference_engine import InferenceEngine
from interfaces import IPreprocessor, IModel


class FakePreprocessor(IPreprocessor):
    def preprocess(self, frame):
        return np.zeros((1, 224, 224, 3), dtype=np.float32)


class FakeModel(IModel):
    def predict(self, tensor):
        return {"logits": np.array([[0.1, 0.5, 0.4]])}   # "clase 1" es la mayor


def test_inference_works():
    pre = FakePreprocessor()
    model = FakeModel()
    class_names = ["A", "B", "C"]

    engine = InferenceEngine(pre, model, class_names)
    label, conf, probs = engine.predict(None)

    assert label == "B"
    assert conf > 0.1
    assert conf < 0.6
    assert len(probs) == 3
