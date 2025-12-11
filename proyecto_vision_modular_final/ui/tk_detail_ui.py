"""
TkDetailUI se encarga de mostrar en una ventana Tkinter el detalle del componente
detectado: imagen, nombre, cantidad en inventario y acceso al datasheet.

- Recibe un IInventoryRepo inyectado (repo) para leer/escribir cantidades.
- Recibe un BaseAssetRegistry inyectado (asset_registry) para obtener imágenes y mapeos.

IMPORTANTE:
AppController llama: ui.show(label, conf, resume_callback)
Por eso show() aquí acepta (class_name, conf, on_retake).
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any

from PIL import Image, ImageTk  # requiere pillow

from interfaces import IDetailUI, IInventoryRepo
from config.assets import BaseAssetRegistry


class TkDetailUI(IDetailUI):
    def __init__(
        self,
        root: tk.Tk,
        repo: IInventoryRepo,
        asset_registry: BaseAssetRegistry,
    ) -> None:
        self._root = root
        self._repo = repo
        self._assets = asset_registry  # inyectado, nada global

        # callback para "volver a lectura" (lo manda el controller)
        self._on_retake: Optional[Callable[[], None]] = None

        # Ventana de detalle (Toplevel sobre root)
        self._window = tk.Toplevel(self._root)
        self._window.title("Detalle del componente")
        self._window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Ocultar al inicio: solo se muestra cuando hay un componente detectado
        self._window.withdraw()

        # ------------------ Widgets principales ------------------
        self._lbl_name = ttk.Label(
            self._window,
            text="Componente: -",
            font=("Arial", 14, "bold"),
        )
        self._lbl_name.pack(pady=5)

        self._lbl_qty = ttk.Label(
            self._window,
            text="Cantidad en inventario: -",
            font=("Arial", 12),
        )
        self._lbl_qty.pack(pady=5)

        self._img_label = ttk.Label(self._window)
        self._img_label.pack(pady=10)

        # ------------------ Zona de botones (+1 / -1 / volver) ------------------
        frame_buttons = ttk.Frame(self._window)
        frame_buttons.pack(pady=10)

        self._btn_minus = ttk.Button(
            frame_buttons, text="-1", command=self._decrease_qty
        )
        self._btn_minus.grid(row=0, column=0, padx=5)

        self._btn_plus = ttk.Button(
            frame_buttons, text="+1", command=self._increase_qty
        )
        self._btn_plus.grid(row=0, column=1, padx=5)

        self._btn_retake = ttk.Button(
            frame_buttons, text="Volver a lectura", command=self._retake_reading
        )
        self._btn_retake.grid(row=0, column=2, padx=5)

        # ------------------ Ingreso manual de cantidad ------------------
        frame_manual = ttk.Frame(self._window)
        frame_manual.pack(pady=5)

        ttk.Label(frame_manual, text="Cantidad manual:").grid(row=0, column=0, padx=5)
        self._entry_qty = ttk.Entry(frame_manual, width=10)
        self._entry_qty.grid(row=0, column=1, padx=5)

        self._btn_apply_manual = ttk.Button(
            frame_manual, text="Aplicar", command=self._apply_manual_qty
        )
        self._btn_apply_manual.grid(row=0, column=2, padx=5)

        self._lbl_error = ttk.Label(
            self._window, text="", foreground="red", font=("Arial", 9)
        )
        self._lbl_error.pack(pady=2)

        # ------------------ Enlace a datasheet ------------------
        self._datasheet_link = ttk.Label(
            self._window,
            text="",
            foreground="blue",
            cursor="hand2",
        )
        self._datasheet_link.pack(pady=8)
        self._datasheet_link.bind("<Button-1>", self._open_datasheet_in_browser)

        # Estado interno
        self._current_photo: Optional[ImageTk.PhotoImage] = None
        self._current_url: Optional[str] = None
        self._current_component_name: Optional[str] = None

    # ------------------------------------------------------------------
    # Implementación del contrato IDetailUI
    # ------------------------------------------------------------------

    def show(self, class_name: str, conf: Any = None, on_retake: Any = None) -> None:
        """
        AppController llama: ui.show(label, conf, resume_callback)

        - conf: puede servir para mostrar confianza (opcional)
        - on_retake: callback que DEBEMOS ejecutar cuando el usuario presione "Volver a lectura"
        """
        # guardar callback (si viene)
        if callable(on_retake):
            self._on_retake = on_retake
        else:
            self._on_retake = None

        # si quisieras mostrar conf, podrías agregar otro label. Por ahora lo ignoramos.
        self.show_component(class_name)

    # ------------------------------------------------------------------
    # API pública propia
    # ------------------------------------------------------------------

    def show_component(self, class_name: str) -> None:
        self._lbl_error.config(text="")
        self._entry_qty.delete(0, tk.END)

        self._current_component_name = class_name
        self._lbl_name.config(text=f"Componente: {class_name}")

        excel_name = self._assets.map_to_excel_name(class_name) or class_name

        try:
            qty = self._repo.read_qty(excel_name)
        except Exception:
            qty = 0
        self._lbl_qty.config(text=f"Cantidad en inventario: {qty}")

        img_path = self._assets.get_image_path(class_name)
        self._update_image(img_path)

        url = self._assets.get_datasheet_url(class_name)
        self._current_url = url
        if url:
            self._datasheet_link.config(text="Ver datasheet", foreground="blue")
        else:
            self._datasheet_link.config(text="(Sin datasheet)", foreground="gray")

        self._window.deiconify()
        self._window.lift()

    def update_inventory_display(self) -> None:
        if not self._current_component_name:
            return

        excel_name = (
            self._assets.map_to_excel_name(self._current_component_name)
            or self._current_component_name
        )
        try:
            qty = self._repo.read_qty(excel_name)
        except Exception:
            qty = 0
        self._lbl_qty.config(text=f"Cantidad en inventario: {qty}")

    # ------------------------------------------------------------------
    # Lógica de botones
    # ------------------------------------------------------------------

    def _increase_qty(self) -> None:
        if not self._current_component_name:
            return

        excel_name = (
            self._assets.map_to_excel_name(self._current_component_name)
            or self._current_component_name
        )
        current = self._repo.read_qty(excel_name)
        self._repo.write_qty(excel_name, current + 1)
        self.update_inventory_display()

    def _decrease_qty(self) -> None:
        if not self._current_component_name:
            return

        excel_name = (
            self._assets.map_to_excel_name(self._current_component_name)
            or self._current_component_name
        )
        current = self._repo.read_qty(excel_name)
        new = max(0, current - 1)
        self._repo.write_qty(excel_name, new)
        self.update_inventory_display()

    def _apply_manual_qty(self) -> None:
        self._lbl_error.config(text="")
        if not self._current_component_name:
            return

        text = self._entry_qty.get().strip()
        if not text:
            return

        try:
            qty = int(text)
        except ValueError:
            msg = f"Entrada inválida '{text}': ingresa solo números enteros."
            print("[TkDetailUI]", msg)
            self._lbl_error.config(text=msg)
            return

        if qty < 0:
            qty = 0

        excel_name = (
            self._assets.map_to_excel_name(self._current_component_name)
            or self._current_component_name
        )
        self._repo.write_qty(excel_name, qty)
        self.update_inventory_display()

    def _retake_reading(self) -> None:
        """
        Botón 'Volver a lectura':
        - Ejecuta el callback que el controller pasó (resume)
        - Oculta la ventana
        """
        # 1) desbloquear controller
        if self._on_retake is not None:
            try:
                self._on_retake()
            except Exception as e:
                print(f"[TkDetailUI] Error al ejecutar callback de retake: {e}")

        # 2) ocultar UI
        self._window.withdraw()

    # ------------------------------------------------------------------
    # Métodos internos de soporte
    # ------------------------------------------------------------------

    def _update_image(self, img_path: Optional[str]) -> None:
        if not img_path:
            self._img_label.config(image="", text="(Sin imagen)")
            self._current_photo = None
            return

        try:
            img = Image.open(img_path)
            img = img.resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            self._img_label.config(image=photo, text="")
            self._current_photo = photo
        except Exception:
            self._img_label.config(image="", text="(Error al cargar imagen)")
            self._current_photo = None

    def _open_datasheet_in_browser(self, event=None) -> None:
        if not self._current_url:
            return
        import webbrowser
        webbrowser.open(self._current_url)

    def _on_close(self) -> None:
        # cerrar = ocultar (y también reanudar, si corresponde)
        if self._on_retake is not None:
            try:
                self._on_retake()
            except Exception:
                pass
        self._window.withdraw()
