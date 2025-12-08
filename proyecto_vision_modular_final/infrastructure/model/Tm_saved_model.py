"""
TMSavedModel se encarga de cargar el modelo de TensorFlow desde disco y exponer un método único,
predict, para ejecutar la inferencia.

    1.- En el constructor verifica que el archivo saved_model.pb exista, intenta cargar la firma
    serving_default y, si algo falla, corta la ejecución con mensajes de error claros.
    2.-Después, con predict, recibe un tensor ya preprocesado y devuelve las salidas del modelo, que
    luego son convertidas en probabilidades y etiquetas por el motor de inferencia.
    Si ocurre algún error durante la inferencia, también corta la ejecución para evitar decisiones
    incorrectas.
"""

import os
import tensorflow as tf

from interfaces import IModel


class TMSavedModel(IModel):
    def __init__(self, model_dir: str) -> None:
        self._model_dir = model_dir
        model_path = os.path.join(model_dir, "saved_model.pb")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"No se encontró el archivo saved_model.pb en {model_path}. "
                "Verifica la ruta SAVEDMODEL_DIR en tu archivo .env."
            )

        try:
            print("Cargando modelo…")
            model = tf.saved_model.load(model_dir)
            self._infer = model.signatures["serving_default"]
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al cargar el modelo: {e}")
            raise

    def predict(self, input_tensor):
        try:
            return self._infer(input_tensor)
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al ejecutar la inferencia del modelo: {e}")
            raise
