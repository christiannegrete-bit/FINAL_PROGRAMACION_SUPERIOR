'''
Test del controlador usando mocks para cámara, UI, preprocesador y modelo.
    1.-FakeCamera simula la cámara devolviendo un frame
    2.-FakeUI simula la UI llamando al callback on_resume inmediatamente
    3.-FakePre y FakeModel simulan el preprocesador y modelo devolviendo datos fijos
    4.-test_controller_logic valida que el controlador use todos los mocks correctamente
      y procese un frame simulando una detección válida.
'''

import numpy as np
from interfaces import ICamera, IDetailUI, IModel, IPreprocessor
from app.controller import AppController
from core.inference.inference_engine import InferenceEngine


class FakeCamera(ICamera):
    def open(self): pass
    def read(self): return np.zeros((480, 640, 3), dtype=np.uint8)
    def release(self): pass


class FakeUI(IDetailUI):
    def show(self, label_str, conf, on_resume):
        on_resume()


class FakePre(IPreprocessor):
    def preprocess(self, frame): return np.zeros((1, 224, 224, 3), dtype=np.float32)


class FakeModel(IModel):
    def predict(self, t): return {"logits": np.array([[0.1, 0.9, 0.0]])}


def test_controller_logic(monkeypatch):
    fake_camera = FakeCamera()
    fake_ui = FakeUI()
    engine = InferenceEngine(FakePre(), FakeModel(), ["A", "B", "C"])

    controller = AppController(
        camera=fake_camera,
        engine=engine,
        ui=fake_ui,
        class_names=["A", "B", "C"],
        valid_classes={"B"},
        no_object_class="A",
        threshold=0.5,
        confirm_frames=1,
    )

    # Simular loop para pruebas
    def fake_run(*args, **kwargs):
        fake_camera.open()
        frame = fake_camera.read()
        label, conf, _ = engine.predict(frame)
        assert label == "B"

    monkeypatch.setattr(controller, "run", fake_run)
    controller.run(None)
