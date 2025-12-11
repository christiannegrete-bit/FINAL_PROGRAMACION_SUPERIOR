"""
GoogleSheetInventoryRepo conecta la aplicación con un inventario almacenado en Google Sheets.

- BaseGoogleSheetRepo:
    Clase base que encapsula la conexión, obtención/creación de la hoja de trabajo y
    utilidades de encabezados. Sus métodos son reutilizados por GoogleSheetInventoryRepo.

- GoogleSheetInventoryRepo:
    Implementación concreta de IInventoryRepo sobre Google Sheets.

Comportamiento:
    1.-ensure_schema verifica que exista la hoja y que tenga las columnas correctas
       ("Componentes", "Cantidad"). Si la hoja está vacía o mal formateada, crea un esquema
       inicial con algunos componentes de ejemplo.
    2.-read_qty lee la cantidad actual para un componente; si no existe la fila, la crea con 0.
    3.-write_qty actualiza o inserta la cantidad, corrigiendo valores negativos.

Si algo falla (credenciales, permisos, estructura), lanza errores claros para evitar
inconsistencias silenciosas.
"""

from typing import List

import gspread
from google.oauth2.service_account import Credentials

from interfaces import IInventoryRepo


class BaseGoogleSheetRepo:
    """Clase base que encapsula conexión y utilidades sobre Google Sheets."""

    def __init__(self, spreadsheet_id: str, worksheet_name: str, credentials_path: str) -> None:
        self._spreadsheet_id = spreadsheet_id
        self._worksheet_name = worksheet_name
        self._credentials_path = credentials_path
        self._ws = self._get_worksheet()

    # ----------------- Métodos reutilizables (herencia real) -----------------

    def _build_client(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(self._credentials_path, scopes=scopes)
        client = gspread.authorize(creds)
        return client

    def _get_worksheet(self):
        """
        Obtiene la worksheet; si no existe, la crea.

        OJO: no recibe parámetros extras, usa los atributos del objeto, así
        evitamos el problema de "takes 3 args but 4 were given".
        """
        client = self._build_client()
        sh = client.open_by_key(self._spreadsheet_id)
        try:
            ws = sh.worksheet(self._worksheet_name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=self._worksheet_name, rows=100, cols=2)
        return ws

    def _ensure_headers(self) -> None:
        """
        Garantiza que la primera fila tenga:
            Componentes | Cantidad

        Si la hoja está vacía, la inicializa con algunos componentes por defecto.
        """
        values: List[List[str]] = self._ws.get_all_values()
        if not values:
            # No hay nada, creamos encabezados y filas de ejemplo
            self._ws.update("A1:B1", [["Componentes", "Cantidad"]])
            default_rows = [
                ["Modulos Rele de Doble canal", 0],
                ["Diodo Zener", 0],
                ["7805", 0],
                ["7404", 0],
            ]
            self._ws.update("A2:B5", default_rows)
            return

        headers = values[0]
        if len(headers) < 2 or headers[0] != "Componentes" or headers[1] != "Cantidad":
            # Reseteamos encabezados pero no borramos datos ya existentes
            self._ws.update("A1:B1", [["Componentes", "Cantidad"]])


class GoogleSheetInventoryRepo(BaseGoogleSheetRepo, IInventoryRepo):
    """Repositorio de inventario que trabaja sobre una hoja de Google Sheets."""

    def __init__(self, spreadsheet_id: str, worksheet_name: str, credentials_path: str) -> None:
        super().__init__(spreadsheet_id, worksheet_name, credentials_path)
        self.ensure_schema()

    # ----------------- API pública del repositorio -----------------

    def ensure_schema(self) -> None:
        """Verifica/crea cabeceras mínimas. Lanza error si algo sale mal."""
        try:
            self._ensure_headers()
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al verificar/crear la hoja de Google Sheets: {e}")
            raise

    def read_qty(self, component_name: str) -> int:
        """
        Lee la cantidad actual para un componente.

        Si la fila no existe, la crea con cantidad 0 y devuelve 0.
        """
        try:
            values = self._ws.get_all_values()
            if not values:
                self._ensure_headers()
                return 0

            rows = values[1:]  # sin encabezado
            for idx, row in enumerate(rows, start=2):  # fila 2 en adelante
                if row and row[0].strip() == component_name:
                    try:
                        return int(row[1])
                    except (ValueError, IndexError):
                        return 0

            # Si no existe, la creamos con cantidad 0
            self._ws.append_row([component_name, 0])
            return 0
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al leer la cantidad desde Google Sheets: {e}")
            raise

    def write_qty(self, component_name: str, qty: int) -> None:
        """
        Actualiza o inserta la cantidad para un componente.

        Si qty < 0, se corrige a 0.
        """
        try:
            if qty < 0:
                qty = 0

            values = self._ws.get_all_values()
            if not values:
                self._ensure_headers()
                values = self._ws.get_all_values()

            rows = values[1:]
            for idx, row in enumerate(rows, start=2):
                if row and row[0].strip() == component_name:
                    self._ws.update_cell(idx, 2, int(qty))
                    break
            else:
                self._ws.append_row([component_name, int(qty)])
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al escribir la cantidad en Google Sheets: {e}")
            raise
