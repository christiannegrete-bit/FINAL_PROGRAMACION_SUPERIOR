"""
El archivo assets.py centraliza todos los recursos asociados a cada componente.

Ahora se usa:

- BaseAssetRegistry: define interfaz y lógica común para trabajar con assets.
- DefaultAssetRegistry: hereda de BaseAssetRegistry y define el contenido concreto
  (imágenes y URLs de datasheets), recibiendo el directorio de imágenes por parámetro.

No hay instancias globales; quien quiera usarlo debe instanciar el registro.
"""

from pathlib import Path
from typing import Dict, Optional


class BaseAssetRegistry:
    """Clase base para manejar recursos de componentes (imágenes, datasheets, nombres Excel)."""

    def __init__(self, img_dir: str) -> None:
        self._img_dir = Path(img_dir)
        self._assets: Dict[str, Dict[str, str]] = {}
        self._excel_name_map: Dict[str, str] = {}

    def get_asset(self, model_name: str) -> Optional[Dict[str, str]]:
        """Devuelve el diccionario de asset para una clase del modelo, o None si no existe."""
        return self._assets.get(model_name)

    def get_image_path(self, model_name: str) -> Optional[str]:
        """Devuelve la ruta de la imagen para una clase del modelo."""
        asset = self.get_asset(model_name)
        return asset.get("img") if asset else None

    def get_datasheet_url(self, model_name: str) -> Optional[str]:
        """Devuelve la URL del datasheet para una clase del modelo."""
        asset = self.get_asset(model_name)
        return asset.get("url") if asset else None

    def map_to_excel_name(self, model_name: str) -> Optional[str]:
        """Traduce el nombre del modelo al nombre usado en el Excel."""
        return self._excel_name_map.get(model_name)

    def list_model_names(self) -> Dict[str, Dict[str, str]]:
        """Devuelve una copia del diccionario completo de assets."""
        return dict(self._assets)

    def list_excel_mappings(self) -> Dict[str, str]:
        """Devuelve una copia del diccionario de mapeos Excel."""
        return dict(self._excel_name_map)


class DefaultAssetRegistry(BaseAssetRegistry):
    """
    Implementación concreta que carga los assets para los componentes conocidos.

    Hereda toda la lógica de acceso de BaseAssetRegistry y solo define los datos.
    """

    def __init__(self, img_dir: str) -> None:
        super().__init__(img_dir=img_dir)

        self._assets = {
            "Modulo Rele 2": {
                "img": str(self._img_dir / "word-image-31183-1.webp"),
                "url": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5773/TS0010D%20DATASHEET.pdf",
            },
            "7404": {
                "img": str(self._img_dir / "74LS04-pinout.jpg"),
                "url": "https://www.ti.com/lit/ds/symlink/sn7404.pdf",
            },
            "Diodo Zener": {
                "img": str(self._img_dir / "Zener-diode-new.png"),
                "url": "https://www.onsemi.com/download/data-sheet/pdf/1n4736at-d.pdf",
            },
            "7805": {
                "img": str(self._img_dir / "7805.jpg"),
                "url": "https://datasheet.octopart.com/L7805CV-STMicroelectronics-datasheet-7264666.pdf",
            },
        }

        self._excel_name_map = {
            "Modulo Rele 2": "Modulos Rele de Doble canal",
            "Diodo Zener":   "Diodo Zener",
            "7805":          "7805",
            "7404":          "7404",
        }
