"""
token_table.py — Tabla de tokens del análisis léxico.

Muestra los resultados del análisis léxico en un Treeview
estilizado con tema oscuro y filas alternadas.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class TokenTable(ctk.CTkFrame):
    """
    Tabla de tokens con columnas: Línea, Token, Tipo, Valor.

    Usa ttk.Treeview con estilo personalizado para integrarse
    con el tema oscuro de la aplicación.
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
            text="  📋 Tokens Encontrados",
            font=("Segoe UI", 14, "bold"),
            text_color="#7aa2f7",
            anchor="w",
        )
        title_label.pack(side="left", padx=10, pady=5)

        self.count_label = ctk.CTkLabel(
            header,
            text="0 tokens",
            font=("Segoe UI", 12),
            text_color="#565f89",
            anchor="e",
        )
        self.count_label.pack(side="right", padx=10, pady=5)

        # ── Estilos del Treeview ─────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Token.Treeview",
            background="#1a1b26",
            foreground="#c0caf5",
            fieldbackground="#1a1b26",
            borderwidth=0,
            font=("Consolas", 12),
            rowheight=28,
        )
        style.configure(
            "Token.Treeview.Heading",
            background="#1e2030",
            foreground="#7aa2f7",
            borderwidth=0,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        style.map(
            "Token.Treeview",
            background=[("selected", "#33467c")],
            foreground=[("selected", "#c0caf5")],
        )
        style.map(
            "Token.Treeview.Heading",
            background=[("active", "#24283b")],
        )

        # ── Treeview ────────────────────────────────────────────────────
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("line", "token", "type", "value"),
            show="headings",
            style="Token.Treeview",
            selectmode="browse",
        )

        # Columnas
        self.tree.heading("line", text="Línea", anchor="center")
        self.tree.heading("token", text="Token", anchor="w")
        self.tree.heading("type", text="Tipo", anchor="w")
        self.tree.heading("value", text="Valor", anchor="w")

        self.tree.column("line", width=60, minwidth=50, anchor="center")
        self.tree.column("token", width=150, minwidth=100, anchor="w")
        self.tree.column("type", width=140, minwidth=100, anchor="w")
        self.tree.column("value", width=150, minwidth=100, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            tree_frame,
            command=self.tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Tags para filas alternadas
        self.tree.tag_configure("odd", background="#1a1b26")
        self.tree.tag_configure("even", background="#1e2030")

    def populate(self, tokens: list[dict]):
        """
        Llena la tabla con los tokens del análisis léxico.

        Args:
            tokens: Lista de dicts con keys: line, token, type, value
        """
        self.clear()

        for i, tok in enumerate(tokens):
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert(
                "",
                "end",
                values=(tok['line'], tok['token'], tok['type'], tok['value']),
                tags=(tag,),
            )

        self.count_label.configure(text=f"{len(tokens)} tokens")

    def clear(self):
        """Limpia la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.count_label.configure(text="0 tokens")
