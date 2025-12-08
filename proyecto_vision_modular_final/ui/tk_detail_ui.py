'''
TkDetailUI es la interfaz gráfica de detalle del componente reconocido.
    1.-Cuando el motor de inferencia detecta algo, llama a show, que abre una ventana con la 
    imagen del componente, el nombre, la confianza y la cantidad actual en Excel.
    2.-Desde esa ventana el usuario puede ver el datasheet, sumar o restar unidades, o añadir 
    una cantidad personalizada, y todos esos cambios se guardan inmediatamente en el Excel.
    3.-Al cerrar con “Volver a lectura”, la UI llama al callback on_resume para que el sistema 
    retome la captura en tiempo real.
'''

from tkinter import (
    Toplevel,
    Label,
    Button,
    LEFT,
    RIGHT,
    TOP,
    simpledialog,
    messagebox,
)
from typing import Callable

from PIL import Image, ImageTk
import webbrowser

from config.assets import ASSETS, EXCEL_NAME_MAP
from interfaces import IDetailUI, IInventoryRepo


class TkDetailUI(IDetailUI):
    def __init__(self, root, repo: IInventoryRepo) -> None:
        self._root = root
        self._repo = repo

    def show(self, label_str: str, conf: float, on_resume: Callable[[], None]) -> None:
        try:
            excel_name = EXCEL_NAME_MAP.get(label_str, label_str)
            current_qty = self._repo.read_qty(excel_name)
        except Exception as e:
            print(f"[ERROR] Ha ocurrido un error al obtener la cantidad desde el repositorio: {e}")
            raise

        info = ASSETS.get(label_str)

        top = Toplevel(self._root)
        top.title(f"{label_str} — conf. {conf:.0%}")

        # Imagen
        if info and info.get("img"):
            try:
                pil_img = Image.open(info["img"])
                max_w = 720
                scale = min(1.0, max_w / pil_img.width)
                pil_img = pil_img.resize(
                    (int(pil_img.width * scale), int(pil_img.height * scale)),
                    Image.LANCZOS,
                )
                tk_img = ImageTk.PhotoImage(pil_img)
                img_label = Label(top, image=tk_img)
                img_label.image = tk_img
                img_label.pack(side=TOP, padx=12, pady=8)
            except Exception as e:
                print(f"[ERROR] Ha ocurrido un error al cargar la imagen de {label_str}: {e}")
                Label(top, text=f"(Error al cargar imagen para {label_str})").pack(
                    side=TOP, pady=8
                )
        else:
            Label(top, text=f"(No se encontró imagen para {label_str})").pack(
                side=TOP, pady=8
            )

        qty_label = Label(
            top,
            text=f"Cantidad actual en Excel: {current_qty}",
            font=("Segoe UI", 12, "bold"),
        )
        qty_label.pack(side=TOP, pady=4)

        def refresh_qty() -> None:
            q = self._repo.read_qty(excel_name)
            qty_label.config(text=f"Cantidad actual en Excel: {q}")

        def add_one() -> None:
            q = self._repo.read_qty(excel_name) + 1
            self._repo.write_qty(excel_name, q)
            refresh_qty()

        def sub_one() -> None:
            q = max(0, self._repo.read_qty(excel_name) - 1)
            self._repo.write_qty(excel_name, q)
            refresh_qty()

        def add_custom() -> None:
            try:
                n = simpledialog.askinteger(
                    "Añadir cantidad",
                    "¿Cuántas unidades deseas añadir?",
                    parent=top,
                    minvalue=1,
                )
                if n is not None:
                    q = self._repo.read_qty(excel_name) + int(n)
                    self._repo.write_qty(excel_name, q)
                    refresh_qty()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")

        if info and info.get("url"):
            Button(
                top,
                text="Ver datasheet",
                command=lambda: webbrowser.open(info["url"], new=2),
                width=18,
            ).pack(side=LEFT, padx=10, pady=12)

        Button(top, text="–1", width=6, command=sub_one).pack(
            side=LEFT, padx=6, pady=12
        )
        Button(top, text="+1", width=6, command=add_one).pack(
            side=LEFT, padx=6, pady=12
        )
        Button(
            top,
            text="Añadir cantidad…",
            width=18,
            command=add_custom,
        ).pack(side=LEFT, padx=10, pady=12)
        Button(
            top,
            text="Volver a lectura",
            width=18,
            command=lambda: (top.destroy(), on_resume()),
        ).pack(side=RIGHT, padx=10, pady=12)

        top.grab_set()
