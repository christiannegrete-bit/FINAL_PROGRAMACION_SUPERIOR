'''
Interfaces que definen los contratos para cada componente del sistema.
    1.-ICamera define los métodos para abrir, leer y liberar la cámara.
    2.-IPreprocessor define el método para preprocesar imágenes antes de la infer
    3.-IModel define el método para ejecutar la inferencia en el modelo de IA.
    4.-IInventoryRepo define los métodos para leer y escribir cantidades en el inventario
    5.-IDetailUI define el método para mostrar la interfaz gráfica de detalle del componente.
    6.-IController define el método para iniciar el flujo principal de la aplicación.
Cada interfaz usa métodos abstractos para garantizar que las implementaciones concretas cumplan
con los contratos necesarios para la correcta interacción entre módulos.
'''

from abc import ABC, abstractmethod
from typing import Any
import numpy as np


class ICamera(ABC):
    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def read(self) -> np.ndarray:
        ...

    @abstractmethod
    def release(self) -> None:
        ...


class IPreprocessor(ABC):
    @abstractmethod
    def preprocess(self, frame: np.ndarray) -> Any:
        ...


class IModel(ABC):
    @abstractmethod
    def predict(self, input_tensor: Any) -> Any:
        ...


class IInventoryRepo(ABC):
    @abstractmethod
    def ensure_schema(self) -> None:
        ...

    @abstractmethod
    def read_qty(self, component_name: str) -> int:
        ...

    @abstractmethod
    def write_qty(self, component_name: str, qty: int) -> None:
        ...


class IDetailUI(ABC):
    @abstractmethod
    def show(self, label_str: str, conf: float, on_resume) -> None:
        ...


class IController(ABC):
    @abstractmethod
    def run(self, root) -> None:
        ...
