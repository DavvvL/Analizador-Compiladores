"""
editor.py — Editor de código con numeración de líneas.

Widget compuesto de CustomTkinter que proporciona un área de
edición de texto con soporte para numeración de líneas sincronizada.
"""

import tkinter as tk
import customtkinter as ctk


class LineNumbers(tk.Canvas):
    """Canvas que muestra los números de línea sincronizados con el editor."""

    def __init__(self, master, text_widget, **kwargs):
        super().__init__(
            master,
            width=50,
            bg="#1a1b26",
            highlightthickness=0,
            **kwargs
        )
        self.text_widget = text_widget
        self._font = ("Consolas", 13)

    def update_line_numbers(self, _event=None):
        """Redibuja los números de línea."""
        self.delete("all")

        # Obtener la primera línea visible
        first_visible = self.text_widget.index("@0,0")
        line_num = int(first_visible.split(".")[0])

        # Recorremos las líneas visibles
        while True:
            dline = self.text_widget.dlineinfo(f"{line_num}.0")
            if dline is None:
                break
            y = dline[1]
            self.create_text(
                45, y,
                anchor="ne",
                text=str(line_num),
                fill="#565f89",
                font=self._font,
            )
            line_num += 1

    def set_theme(self, is_dark: bool):
        """Actualiza colores según el tema."""
        if is_dark:
            self.configure(bg="#1a1b26")
        else:
            self.configure(bg="#e8e8e8")


class CodeEditor(ctk.CTkFrame):
    """
    Editor de código completo con numeración de líneas y resaltado.

    Componentes:
    - Canvas de números de línea (izquierda)
    - Área de texto editable (derecha)
    """

    # Palabras reservadas para resaltado
    KEYWORDS = {
        'def', 'if', 'elif', 'else', 'while', 'for', 'in',
        'return', 'print', 'and', 'or', 'not', 'True', 'False', 'None',
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Fuente monoespaciada
        self._font = ("Consolas", 13)
        self._ready = False  # Guard para callbacks durante inicialización

        # ── Layout ───────────────────────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Text Widget (usar tk.Text para mayor control) ───────────────
        self._text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._text_frame.grid(row=0, column=1, sticky="nsew")
        self._text_frame.grid_rowconfigure(0, weight=1)
        self._text_frame.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            self._text_frame,
            wrap="none",
            font=self._font,
            bg="#1a1b26",
            fg="#c0caf5",
            insertbackground="#7aa2f7",
            selectbackground="#33467c",
            selectforeground="#c0caf5",
            relief="flat",
            padx=10,
            pady=10,
            undo=True,
            tabs="    ",
            borderwidth=0,
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        # ── Line Numbers (crear ANTES de scrollbar para evitar callbacks tempranos)
        self.line_numbers = LineNumbers(self, self.text)
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        # Scrollbar
        self._scrollbar = ctk.CTkScrollbar(
            self._text_frame,
            command=self.text.yview,
        )
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=self._sync_scroll)

        # Scrollbar horizontal
        self._h_scrollbar = ctk.CTkScrollbar(
            self._text_frame,
            command=self.text.xview,
            orientation="horizontal",
        )
        self._h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.text.configure(xscrollcommand=self._h_scrollbar.set)

        # ── Tags de resaltado ────────────────────────────────────────────
        self.text.tag_configure("keyword", foreground="#bb9af7")
        self.text.tag_configure("builtin", foreground="#7dcfff")
        self.text.tag_configure("string", foreground="#9ece6a")
        self.text.tag_configure("number", foreground="#ff9e64")
        self.text.tag_configure("comment", foreground="#565f89", font=(self._font[0], self._font[1], "italic"))
        self.text.tag_configure("operator", foreground="#89ddff")
        self.text.tag_configure("boolean", foreground="#ff9e64")

        # ── Bindings ────────────────────────────────────────────────────
        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<MouseWheel>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<Tab>", self._handle_tab)

        # Marcar como listo y actualización inicial
        self._ready = True
        self.after(100, self._on_change)

    def _sync_scroll(self, *args):
        """Sincroniza scrollbar y números de línea."""
        self._scrollbar.set(*args)
        if hasattr(self, 'line_numbers'):
            self.line_numbers.update_line_numbers()

    def _on_change(self, event=None):
        """Actualiza números de línea y resaltado en cada cambio."""
        if hasattr(self, 'line_numbers'):
            self.line_numbers.update_line_numbers()
        self._highlight_syntax()

    def _handle_tab(self, event):
        """Inserta 4 espacios en lugar de tab."""
        self.text.insert("insert", "    ")
        return "break"

    def _highlight_syntax(self):
        """Resaltado sintáctico básico."""
        # Remover tags anteriores
        for tag in ("keyword", "builtin", "string", "number", "comment", "operator", "boolean"):
            self.text.tag_remove(tag, "1.0", "end")

        content = self.text.get("1.0", "end-1c")
        lines = content.split("\n")

        for line_idx, line in enumerate(lines, start=1):
            col = 0
            i = 0
            while i < len(line):
                ch = line[i]

                # Comentarios
                if ch == '#':
                    start = f"{line_idx}.{i}"
                    end = f"{line_idx}.{len(line)}"
                    self.text.tag_add("comment", start, end)
                    break

                # Strings
                if ch in ('"', "'"):
                    quote = ch
                    start_col = i
                    i += 1
                    while i < len(line) and line[i] != quote:
                        if line[i] == '\\':
                            i += 1
                        i += 1
                    i += 1  # cerrar comilla
                    start = f"{line_idx}.{start_col}"
                    end = f"{line_idx}.{i}"
                    self.text.tag_add("string", start, end)
                    continue

                # Números
                if ch.isdigit():
                    start_col = i
                    while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                        i += 1
                    start = f"{line_idx}.{start_col}"
                    end = f"{line_idx}.{i}"
                    self.text.tag_add("number", start, end)
                    continue

                # Identificadores y palabras clave
                if ch.isalpha() or ch == '_':
                    start_col = i
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        i += 1
                    word = line[start_col:i]
                    start = f"{line_idx}.{start_col}"
                    end = f"{line_idx}.{i}"
                    if word in self.KEYWORDS:
                        self.text.tag_add("keyword", start, end)
                    elif word in ('True', 'False', 'None'):
                        self.text.tag_add("boolean", start, end)
                    elif word in ('print', 'len', 'range', 'int', 'float', 'str', 'input', 'type', 'abs'):
                        self.text.tag_add("builtin", start, end)
                    continue

                # Operadores
                if ch in ('=', '!', '<', '>', '+', '-', '*', '/'):
                    start_col = i
                    if i + 1 < len(line) and line[i + 1] == '=':
                        i += 2
                    else:
                        i += 1
                    start = f"{line_idx}.{start_col}"
                    end = f"{line_idx}.{i}"
                    self.text.tag_add("operator", start, end)
                    continue

                i += 1

    def get_code(self) -> str:
        """Retorna el contenido del editor."""
        return self.text.get("1.0", "end-1c")

    def set_code(self, code: str):
        """Establece el contenido del editor."""
        self.text.delete("1.0", "end")
        self.text.insert("1.0", code)
        self._on_change()

    def clear(self):
        """Limpia el editor."""
        self.text.delete("1.0", "end")
        self._on_change()
