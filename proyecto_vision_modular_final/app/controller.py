import time
from typing import Set, List

import cv2

from core.inference.inference_engine import InferenceEngine
from interfaces import ICamera, IDetailUI, IController


class AppController(IController):
    def __init__(self, camera: ICamera,engine: InferenceEngine,ui: IDetailUI,class_names: List[str],
                 valid_classes: Set[str],no_object_class: str,threshold: float,confirm_frames: int,) -> None:
        self._camera = camera
        self._engine = engine
        self._ui = ui
        self._class_names = class_names
        self._valid_classes = valid_classes
        self._no_object_class = no_object_class
        self._threshold = threshold
        self._confirm_frames = confirm_frames

        self._paused = False
        self._last_label = None
        self._streak = 0

    def _resume(self) -> None:
        self._paused = False
        self._last_label = None
        self._streak = 0

    def run(self, root) -> None:
        try:
            self._camera.open()
        except Exception:
            # El error ya se imprimió en la cámara
            return

        print("Ventana de cámara activa. Pulsa 'q' para salir.")

        try:
            while True:
                if not self._paused:
                    try:
                        frame = self._camera.read()
                    except Exception:
                        break

                    label, conf, _ = self._engine.predict(frame)

                    overlay = frame.copy()
                    color = (
                        (0, 255, 0)
                        if (label in self._valid_classes and conf >= self._threshold)
                        else (0, 200, 255)
                    )
                    cv2.putText(
                        overlay,
                        f"{label} ({conf:.2f})",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        color,
                        2,
                        cv2.LINE_AA,
                    )
                    cv2.imshow("Teachable Machine - Cam", overlay)

                    if label == self._no_object_class:
                        self._last_label, self._streak = None, 0
                    else:
                        if label in self._valid_classes and conf >= self._threshold:
                            if label == self._last_label:
                                self._streak += 1
                            else:
                                self._last_label, self._streak = label, 1

                            if self._streak >= self._confirm_frames:
                                self._paused = True
                                root.after(
                                    0,
                                    self._ui.show,
                                    label,
                                    conf,
                                    self._resume,
                                )
                                while self._paused:
                                    root.update()
                                    if (cv2.waitKey(1) & 0xFF) == ord("q"):
                                        self._paused = False
                                        raise KeyboardInterrupt
                                    time.sleep(0.01)
                        else:
                            self._last_label, self._streak = None, 0

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                root.update_idletasks()
                root.update()

        except KeyboardInterrupt:
            print("Saliendo…")
        finally:
            try:
                self._camera.release()
            except Exception:
                pass
            cv2.destroyAllWindows()
            try:
                root.destroy()
            except Exception:
                pass
