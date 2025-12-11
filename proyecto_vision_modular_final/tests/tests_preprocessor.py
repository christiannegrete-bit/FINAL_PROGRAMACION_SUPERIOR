'''
Estos tests verifican que TMPreprocessor funcione correctamente.
'''
import numpy as np
from core.preprocessing.Tm_preprocessor import TMPreprocessor

def test_preprocess_basic():
    prep = TMPreprocessor(224)

    # Frame falso (como si viniera de la cámara)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    out = prep.preprocess(fake_frame)

    # El tensor debe tener shape: (1, 224, 224, 3)
    assert out.shape == (1, 224, 224, 3)
    assert out.dtype == np.float32
    # Valores deben estar entre 0 y 1
    assert out.min() >= 0.0 and out.max() <= 1.0
def test_preprocess_color_conversion():
    prep = TMPreprocessor(128)

    # Crear un frame con un color específico en BGR
    blue_bgr = np.array([[[255, 0, 0]]], dtype=np.uint8)  # Azul en BGR
    blue_frame = np.tile(blue_bgr, (240, 320, 1))  # Frame 240x320

    out = prep.preprocess(blue_frame)

    # El color debe convertirse a RGB
    # El pixel central del tensor preprocesado debería ser azul en RGB
    center_pixel = out[0, 64, 64]  # Coordenadas centrales en el tamaño 128x128
    r, g, b = center_pixel
    assert r < 0.1 and g < 0.1 and b > 0.9  # Azul en RGB normalizado