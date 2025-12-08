'''
ExcelInventoryRepo es el módulo que conecta la aplicación con el inventario en Excel.
    1.-Con ensure_schema se asegura de que el archivo exista y tenga las columnas correctas.
    2.-read_qty permite leer la cantidad actual de un componente, y si el componente no está en 
    la tabla, lo crea con cantidad 0.
    3.-write_qty actualiza o inserta la cantidad en el Excel, corrigiendo valores negativos y 
    guardando siempre la estructura normalizada.
Si algo falla en lectura o escritura, lanza errores claros y detiene el flujo para evitar 
inconsistencias en los datos.
'''

import os
import pandas as pd
from interfaces import IInventoryRepo


class ExcelInventoryRepo(IInventoryRepo):
    def __init__(self, path: str) -> None:
        self._path = path
        self.ensure_schema()

    # ----------------------------------------------------------
    # Método estático para normalizar columnas
    # ----------------------------------------------------------
    @staticmethod
    def _normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
        cols = [c.strip() for c in df.columns]
        df.columns = cols

        if "Componentes" not in df.columns or "Cantidad" not in df.columns:
            raise ValueError("El Excel debe tener columnas: 'Componentes' y 'Cantidad'.")

        return df

    # ----------------------------------------------------------
    # Crear o validar la estructura del Excel
    # ----------------------------------------------------------
    def ensure_schema(self) -> None:
        try:
            if not os.path.exists(self._path):
                # Crear archivo desde cero
                data = {
                    "Componentes": [
                        "Modulos Rele de Doble canal",
                        "Diodo Zener",
                        "7805",
                        "7404",
                    ],
                    "Cantidad": [0, 0, 0, 0],
                }
                df = pd.DataFrame(data)
                df.to_excel(self._path, index=False)

            else:
                try:
                    df = pd.read_excel(self._path)
                    ExcelInventoryRepo._normalize_df_columns(df)

                except Exception:
                    # Corrompido → lo creamos otra vez
                    data = {
                        "Componentes": [
                            "Modulos Rele de Doble canal",
                            "Diodo Zener",
                            "7805",
                            "7404",
                        ],
                        "Cantidad": [0, 0, 0, 0],
                    }
                    pd.DataFrame(data).to_excel(self._path, index=False)

        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al verificar/crear el Excel: {e}")
            raise

    # ----------------------------------------------------------
    # Leer cantidad
    # ----------------------------------------------------------
    def read_qty(self, component_name: str) -> int:
        try:
            df = pd.read_excel(self._path)
            df = ExcelInventoryRepo._normalize_df_columns(df)

            row = df.loc[df["Componentes"].astype(str).str.strip() == component_name]

            if row.empty:
                # Si no existe, lo agregamos con 0
                df.loc[len(df)] = [component_name, 0]
                df.to_excel(self._path, index=False)
                return 0

            return int(row["Cantidad"].iloc[0])

        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al leer la cantidad desde el Excel: {e}")
            raise

    # ----------------------------------------------------------
    # Escribir cantidad
    # ----------------------------------------------------------
    def write_qty(self, component_name: str, qty: int) -> None:
        try:
            if qty < 0:
                qty = 0

            df = pd.read_excel(self._path)
            df = ExcelInventoryRepo._normalize_df_columns(df)

            mask = df["Componentes"].astype(str).str.strip() == component_name

            if not mask.any():
                df.loc[len(df)] = [component_name, qty]
            else:
                df.loc[mask, "Cantidad"] = int(qty)

            df.to_excel(self._path, index=False)

        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al escribir la cantidad en el Excel: {e}")
            raise
