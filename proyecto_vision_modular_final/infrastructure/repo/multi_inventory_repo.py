"""
MultiInventoryRepo sincroniza varios repositorios de inventario al mismo tiempo.

Implementa IInventoryRepo y delega:
    - read_qty: al primer repositorio de la lista (la "fuente principal").
    - write_qty: a TODOS los repos (ej. Excel + Google Sheets).

Si alguno falla en write_qty, muestra el error pero intenta seguir con los demás,
para evitar que un backend externo deje al sistema inconsistente.
"""

from typing import List

from interfaces import IInventoryRepo


class MultiInventoryRepo(IInventoryRepo):
    def __init__(self, repos: List[IInventoryRepo]) -> None:
        if not repos:
            raise ValueError("MultiInventoryRepo requiere al menos un repositorio interno.")
        self._repos = repos

    def ensure_schema(self) -> None:
        """
        Asegura que todos los repos internos tengan su estructura lista.
        """
        for repo in self._repos:
            repo.ensure_schema()

    def read_qty(self, component_name: str) -> int:
        """
        Lee siempre del primer repositorio (fuente principal).
        """
        return self._repos[0].read_qty(component_name)

    def write_qty(self, component_name: str, qty: int) -> None:
        """
        Escribe en TODOS los repos.

        Si alguno falla, muestra el error, pero intenta seguir con los demás
        para no depender de un solo backend externo.
        """
        errors = []
        for repo in self._repos:
            try:
                repo.write_qty(component_name, qty)
            except Exception as e:
                repo_name = type(repo).__name__
                print(f"[WARN] Falló write_qty en {repo_name}: {e}")
                errors.append((repo_name, e))

        if errors:
            # Opcional: puedes decidir si quieres elevar una excepción global
            # o solo loguear. Por ahora solo logueamos.
            pass
