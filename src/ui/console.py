"""
console.py — Consola de salida para el análisis semántico.

Área de texto de solo lectura estilizada como terminal,
con soporte para mensajes coloreados (éxito/error/info).
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime


class OutputConsole(ctk.CTkFrame):
    """
    Consola de salida estilizada como terminal.

    Muestra mensajes de éxito (verde), error (rojo) e info (azul)
    con timestamps.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ── Layout ───────────────────────────────────────────────────────
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#1e2030", height=40, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        title_label = ctk.CTkLabel(
            header,
            text="  🖥️ Consola — Análisis Semántico",
            font=("Segoe UI", 14, "bold"),
            text_color="#e0af68",
            anchor="w",
        )
        title_label.pack(side="left", padx=10, pady=5)

        # Botón limpiar
        btn_clear = ctk.CTkButton(
            header,
            text="Limpiar",
            width=70, height=26,
            command=self.clear,
            fg_color="#33467c",
            hover_color="#3d4f8f",
            font=("Segoe UI", 11),
        )
        btn_clear.pack(side="right", padx=10, pady=5)

        # ── Text Widget ─────────────────────────────────────────────────
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            text_frame,
            wrap="word",
            font=("Consolas", 12),
            bg="#16161e",
            fg="#c0caf5",
            insertbackground="#c0caf5",
            relief="flat",
            padx=15,
            pady=10,
            borderwidth=0,
            state="disabled",
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            text_frame,
            command=self.text.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        # ── Tags de color ────────────────────────────────────────────────
        self.text.tag_configure("success", foreground="#9ece6a")
        self.text.tag_configure("error", foreground="#f7768e")
        self.text.tag_configure("warning", foreground="#e0af68")
        self.text.tag_configure("info", foreground="#7aa2f7")
        self.text.tag_configure("timestamp", foreground="#565f89")
        self.text.tag_configure("separator", foreground="#33467c")
        self.text.tag_configure("header", foreground="#bb9af7", font=("Consolas", 12, "bold"))

    def _write(self, text: str, tag: str = ""):
        """Escribe texto en la consola."""
        self.text.configure(state="normal")
        if tag:
            self.text.insert("end", text, tag)
        else:
            self.text.insert("end", text)
        self.text.configure(state="disabled")
        self.text.see("end")

    def _timestamp(self):
        """Inserta un timestamp."""
        now = datetime.now().strftime("%H:%M:%S")
        self._write(f"[{now}] ", "timestamp")

    def write_header(self, text: str):
        """Escribe un encabezado de sección."""
        self._write("\n", "")
        self._write("═" * 50 + "\n", "separator")
        self._timestamp()
        self._write(f"{text}\n", "header")
        self._write("═" * 50 + "\n", "separator")

    def write_success(self, text: str):
        """Escribe un mensaje de éxito (verde)."""
        self._timestamp()
        self._write(f"✅ {text}\n", "success")

    def write_error(self, text: str):
        """Escribe un mensaje de error (rojo)."""
        self._timestamp()
        self._write(f"❌ {text}\n", "error")

    def write_warning(self, text: str):
        """Escribe un mensaje de advertencia (amarillo)."""
        self._timestamp()
        self._write(f"⚠️  {text}\n", "warning")

    def write_info(self, text: str):
        """Escribe un mensaje informativo (azul)."""
        self._timestamp()
        self._write(f"ℹ️  {text}\n", "info")

    def write_plain(self, text: str):
        """Escribe texto plano."""
        self._write(f"   {text}\n")

    def clear(self):
        """Limpia la consola."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def show_semantic_results(self, errors: list[str]):
        """
        Muestra los resultados del análisis semántico.

        Args:
            errors: Lista de errores. Vacía = éxito.
        """
        self.write_header("ANÁLISIS SEMÁNTICO")

        if not errors:
            self.write_success("Análisis semántico exitoso — No se encontraron errores")
            self.write_info(f"El código es semánticamente válido")
        else:
            self.write_error(f"Se encontraron {len(errors)} error(es) semántico(s):")
            self._write("\n")
            for i, err in enumerate(errors, 1):
                self._timestamp()
                self._write(f"  {i}. {err}\n", "error")
            self._write("\n")
            self.write_warning("Corrija los errores anteriores para un análisis exitoso")

    def show_syntax_results(self, errors: list[str]):
        """Muestra resultados del análisis sintáctico."""
        self.write_header("ANÁLISIS SINTÁCTICO")

        if not errors:
            self.write_success("Análisis sintáctico exitoso — AST generado correctamente")
        else:
            self.write_error(f"Se encontraron {len(errors)} error(es) de sintaxis:")
            self._write("\n")
            for i, err in enumerate(errors, 1):
                self._timestamp()
                self._write(f"  {i}. {err}\n", "error")

    def show_lexer_results(self, token_count: int):
        """Muestra resumen del análisis léxico."""
        self.write_header("ANÁLISIS LÉXICO")
        self.write_success(f"Análisis léxico exitoso — {token_count} token(s) identificados")
