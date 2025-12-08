"""
El archivo assets.py centraliza todos los recursos asociados a cada componente.
    1.-El diccionario ASSETS enlaza cada clase del modelo con su imagen y datasheet, que la interfaz 
    usa para mostrar la información detallada.
    2.-El diccionario EXCEL_NAME_MAP traduce los nombres del modelo a los nombres exactos usados en 
    el Excel, garantizando que el inventario se actualice correctamente sin errores de texto.
"""

import os
from pathlib import Path

from .settings import SETTINGS

# Directorio base de imágenes
IMG_DIR_PATH = Path(SETTINGS.IMG_DIR)

ASSETS = {
    "Modulo Rele 2": {
        "img": str(IMG_DIR_PATH / "word-image-31183-1.webp"),
        "url": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5773/TS0010D%20DATASHEET.pdf",
    },
    "7404": {
        "img": str(IMG_DIR_PATH / "74LS04-pinout.jpg"),
        "url": "https://www.ti.com/lit/ds/symlink/sn7404.pdf",
    },
    "Diodo Zener": {
        "img": str(IMG_DIR_PATH / "Zener-diode-new.png"),
        "url": "https://www.onsemi.com/download/data-sheet/pdf/1n4736at-d.pdf",
    },
    "7805": {
        "img": str(IMG_DIR_PATH / "7805.jpg"),
        "url": "https://datasheet.octopart.com/L7805CV-STMicroelectronics-datasheet-7264666.pdf",
    },
}

EXCEL_NAME_MAP = {
    "Modulo Rele 2": "Modulos Rele de Doble canal",
    "Diodo Zener":   "Diodo Zener",
    "7805":          "7805",
    "7404":          "7404",
}
