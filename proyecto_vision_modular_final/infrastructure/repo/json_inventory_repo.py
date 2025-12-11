'''
Json InventoryRepo es el módulo que conecta la aplicación con el inventario en Json.
    1.-Verifica que exista un archivo json si no lo crea .
    2.-Permite escribir la clase reconocida .
    3.-write_qty actualiza o inserta la cantidad en el json, corrigiendo valores negativos y 
    guardando siempre la estructura normalizada.
    4._read_qty permite leer la cantidad actual de un componente, y si el componente no está en
Si algo falla en lectura o escritura, lanza errores claros y detiene el flujo para evitar 
inconsistencias en los datos.
'''

import os
import json
from interfaces import IInventoryRepo
class JsonInventoryRepo(IInventoryRepo):
    def __init__(self, path: str) -> None:
        self._path = path
        self.ensure_schema()

    def ensure_schema(self) -> None:
        try:
            if not os.path.exists(self._path):
                initial_data = {
                    "Modulos Rele de Doble canal": 0,
                    "Diodo Zener": 0,
                    "7805": 0,
                    "7404": 0,
                }
                with open(self._path, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=4)
            else:
                with open(self._path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("El archivo JSON debe contener un objeto.")
        except Exception as e:
            raise RuntimeError(f"Error al asegurar el esquema del inventario JSON: {e}")

    def read_qty(self, component_name: str) -> int:
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(component_name, 0)
        except Exception as e:
            raise RuntimeError(f"Error al leer la cantidad del componente '{component_name}': {e}")

    def write_qty(self, component_name: str, qty: int) -> None:
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data[component_name] = max(0, qty)
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Error al escribir la cantidad del componente '{component_name}': {e}")


