"""
ast_canvas.py — Visualización del Árbol de Sintaxis Abstracta.

Dibuja el AST en un Canvas de tkinter con nodos coloreados por tipo,
líneas de conexión y soporte para scroll/zoom.
"""

import tkinter as tk
import customtkinter as ctk
from ..ast_nodes import (
    ASTNode, ProgramNode, AssignNode, FunctionDefNode, IfNode, WhileNode,
    ReturnNode, PrintNode, ExprStmtNode, BinOpNode, UnaryOpNode,
    ComparisonNode, BoolOpNode, NotNode, NumberNode, FloatNode,
    StringNode, BoolNode, NoneNode, IdentifierNode, FunctionCallNode,
    ListNode, ElifNode, ElseNode, ConditionWrapper, ParamsNode, ForNode,
)


# ── Colores por tipo de nodo ─────────────────────────────────────────────

NODE_COLORS = {
    # Programa
    "ProgramNode": ("#7aa2f7", "#1a1b26"),       # Azul
    # Sentencias
    "AssignNode": ("#7dcfff", "#1a1b26"),         # Cyan
    "FunctionDefNode": ("#bb9af7", "#1a1b26"),    # Púrpura
    "IfNode": ("#ff9e64", "#1a1b26"),             # Naranja
    "ElifNode": ("#ff9e64", "#1a1b26"),
    "ElseNode": ("#ff9e64", "#1a1b26"),
    "WhileNode": ("#f7768e", "#1a1b26"),          # Rosa
    "ForNode": ("#f7768e", "#1a1b26"),
    "ReturnNode": ("#e0af68", "#1a1b26"),         # Amarillo
    "PrintNode": ("#9ece6a", "#1a1b26"),          # Verde
    "ExprStmtNode": ("#565f89", "#c0caf5"),       # Gris
    "ConditionWrapper": ("#ff9e64", "#1a1b26"),
    "ParamsNode": ("#bb9af7", "#1a1b26"),
    # Expresiones
    "BinOpNode": ("#89ddff", "#1a1b26"),          # Cyan claro
    "UnaryOpNode": ("#89ddff", "#1a1b26"),
    "ComparisonNode": ("#7dcfff", "#1a1b26"),
    "BoolOpNode": ("#bb9af7", "#1a1b26"),
    "NotNode": ("#bb9af7", "#1a1b26"),
    "FunctionCallNode": ("#9ece6a", "#1a1b26"),   # Verde
    "ListNode": ("#7dcfff", "#1a1b26"),
    # Literales
    "NumberNode": ("#ff9e64", "#1a1b26"),          # Naranja
    "FloatNode": ("#ff9e64", "#1a1b26"),
    "StringNode": ("#9ece6a", "#1a1b26"),          # Verde
    "BoolNode": ("#ff9e64", "#1a1b26"),
    "NoneNode": ("#565f89", "#c0caf5"),
    "IdentifierNode": ("#c0caf5", "#1a1b26"),      # Blanco
}

DEFAULT_COLORS = ("#565f89", "#c0caf5")


# ── Cálculo del layout del árbol ──────────────────────────────────────

class TreeLayout:
    """
    Calcula las posiciones (x, y) de los nodos del AST usando
    un algoritmo de distribución simétrica por niveles.
    """

    NODE_WIDTH = 130
    NODE_HEIGHT = 40
    H_SPACING = 20
    V_SPACING = 70

    def __init__(self):
        self.positions: dict[int, tuple[float, float]] = {}
        self._node_id = 0
        self._node_map: dict[int, ASTNode] = {}

    def compute(self, root: ASTNode) -> tuple[dict, dict, float, float]:
        """
        Calcula el layout del árbol.

        Returns:
            (positions, node_map, total_width, total_height)
        """
        self.positions = {}
        self._node_id = 0
        self._node_map = {}

        if root is None:
            return {}, {}, 0, 0

        width = self._compute_subtree_width(root)
        self._assign_positions(root, width / 2, 40, 0)

        total_w = max(pos[0] for pos in self.positions.values()) + self.NODE_WIDTH + 40
        total_h = max(pos[1] for pos in self.positions.values()) + self.NODE_HEIGHT + 60

        return self.positions, self._node_map, total_w, total_h

    def _get_id(self, node: ASTNode) -> int:
        nid = self._node_id
        self._node_id += 1
        self._node_map[nid] = node
        return nid

    def _compute_subtree_width(self, node: ASTNode) -> float:
        """Calcula el ancho total del subárbol."""
        children = node.children()
        if not children:
            return self.NODE_WIDTH + self.H_SPACING

        child_widths = [self._compute_subtree_width(c) for c in children]
        return max(sum(child_widths), self.NODE_WIDTH + self.H_SPACING)

    def _assign_positions(self, node: ASTNode, center_x: float, y: float, depth: int):
        """Asigna posiciones recursivamente."""
        nid = self._get_id(node)
        self.positions[nid] = (center_x, y)

        children = node.children()
        if not children:
            return

        child_widths = [self._compute_subtree_width(c) for c in children]
        total_width = sum(child_widths)

        start_x = center_x - total_width / 2
        child_y = y + self.NODE_HEIGHT + self.V_SPACING

        for i, child in enumerate(children):
            child_center = start_x + child_widths[i] / 2
            self._assign_positions(child, child_center, child_y, depth + 1)
            start_x += child_widths[i]


# ── Widget del Canvas ────────────────────────────────────────────────────

class ASTCanvas(ctk.CTkFrame):
    """
    Canvas interactivo para visualizar el AST.

    Características:
    - Nodos coloreados por tipo
    - Líneas de conexión curvas
    - Scroll (arrastrar) y zoom
    - Botones de zoom in/out/reset
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ── Layout ───────────────────────────────────────────────────────
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Toolbar ──────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="#1e2030", height=40, corner_radius=0)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        title_label = ctk.CTkLabel(
            toolbar,
            text="  🌳 Árbol de Sintaxis Abstracta (AST)",
            font=("Segoe UI", 14, "bold"),
            text_color="#9ece6a",
            anchor="w",
        )
        title_label.pack(side="left", padx=10, pady=5)

        # Zoom controls
        zoom_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        zoom_frame.pack(side="right", padx=10)

        self._zoom_level = 1.0

        btn_zoom_in = ctk.CTkButton(
            zoom_frame, text="🔍+", width=35, height=28,
            command=self._zoom_in,
            fg_color="#33467c", hover_color="#3d4f8f",
            font=("Segoe UI", 13),
        )
        btn_zoom_in.pack(side="left", padx=2)

        btn_zoom_out = ctk.CTkButton(
            zoom_frame, text="🔍−", width=35, height=28,
            command=self._zoom_out,
            fg_color="#33467c", hover_color="#3d4f8f",
            font=("Segoe UI", 13),
        )
        btn_zoom_out.pack(side="left", padx=2)

        btn_reset = ctk.CTkButton(
            zoom_frame, text="⟳", width=35, height=28,
            command=self._zoom_reset,
            fg_color="#33467c", hover_color="#3d4f8f",
            font=("Segoe UI", 14),
        )
        btn_reset.pack(side="left", padx=2)

        # ── Canvas ──────────────────────────────────────────────────────
        canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#16161e",
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        h_scroll = ctk.CTkScrollbar(
            canvas_frame,
            command=self.canvas.xview,
            orientation="horizontal",
        )
        h_scroll.grid(row=1, column=0, sticky="ew")

        v_scroll = ctk.CTkScrollbar(
            canvas_frame,
            command=self.canvas.yview,
        )
        v_scroll.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set,
        )

        # ── Pan (arrastrar) ─────────────────────────────────────────────
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._do_pan)
        self.canvas.bind("<MouseWheel>", self._scroll_zoom)

        self._pan_data = {"x": 0, "y": 0}

        # Mensaje inicial
        self._show_placeholder()

    def _show_placeholder(self):
        """Muestra mensaje cuando no hay AST."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 500
        h = self.canvas.winfo_height() or 400
        self.canvas.create_text(
            w // 2, h // 2,
            text="Analiza el código para\nvisualizar el AST aquí",
            fill="#565f89",
            font=("Segoe UI", 16),
            justify="center",
        )

    def draw_ast(self, root: ASTNode):
        """Dibuja el AST completo en el canvas."""
        self.canvas.delete("all")
        self._zoom_level = 1.0

        if root is None:
            self._show_placeholder()
            return

        layout = TreeLayout()
        positions, node_map, total_w, total_h = layout.compute(root)

        if not positions:
            self._show_placeholder()
            return

        # Configurar scroll region
        padding = 60
        self.canvas.configure(
            scrollregion=(0, 0, total_w + padding, total_h + padding)
        )

        # Dibujar conexiones primero (debajo de nodos)
        self._draw_connections(positions, node_map)

        # Dibujar nodos
        self._draw_nodes(positions, node_map)

    def _draw_connections(self, positions, node_map):
        """Dibuja las líneas entre nodos padre-hijo."""
        for nid, node in node_map.items():
            px, py = positions[nid]
            children = node.children()

            for child in children:
                # Encontrar el ID del hijo
                for cid, cnode in node_map.items():
                    if cnode is child:
                        cx, cy = positions[cid]
                        # Línea curva con punto medio
                        mid_y = (py + TreeLayout.NODE_HEIGHT + cy) / 2
                        self.canvas.create_line(
                            px, py + TreeLayout.NODE_HEIGHT / 2 + 15,
                            px, mid_y,
                            cx, mid_y,
                            cx, cy - TreeLayout.NODE_HEIGHT / 2 + 5,
                            fill="#33467c",
                            width=2,
                            smooth=True,
                        )
                        break

    def _draw_nodes(self, positions, node_map):
        """Dibuja los nodos del AST como rectángulos redondeados."""
        for nid, node in node_map.items():
            x, y = positions[nid]
            label = node.label()
            type_name = type(node).__name__
            bg_color, fg_color = NODE_COLORS.get(type_name, DEFAULT_COLORS)

            # Dimensiones del nodo
            text_len = max(len(label.split('\n')[0]) * 8 + 20, 80)
            half_w = text_len / 2
            half_h = 18

            # Sombra
            self.canvas.create_rectangle(
                x - half_w + 3, y - half_h + 3,
                x + half_w + 3, y + half_h + 3,
                fill="#0f0f14",
                outline="",
            )

            # Nodo (rectángulo redondeado simulado)
            self.canvas.create_rectangle(
                x - half_w, y - half_h,
                x + half_w, y + half_h,
                fill="#24283b",
                outline=bg_color,
                width=2,
            )

            # Texto
            self.canvas.create_text(
                x, y,
                text=label,
                fill=bg_color,
                font=("Consolas", 10, "bold"),
                justify="center",
            )

    def _start_pan(self, event):
        self._pan_data["x"] = event.x
        self._pan_data["y"] = event.y

    def _do_pan(self, event):
        dx = event.x - self._pan_data["x"]
        dy = event.y - self._pan_data["y"]
        self.canvas.xview_scroll(-dx, "units")
        self.canvas.yview_scroll(-dy, "units")
        self._pan_data["x"] = event.x
        self._pan_data["y"] = event.y

    def _scroll_zoom(self, event):
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def _zoom_in(self):
        self._zoom_level *= 1.2
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        self._update_scroll_region()

    def _zoom_out(self):
        self._zoom_level /= 1.2
        self.canvas.scale("all", 0, 0, 1 / 1.2, 1 / 1.2)
        self._update_scroll_region()

    def _zoom_reset(self):
        factor = 1 / self._zoom_level
        self.canvas.scale("all", 0, 0, factor, factor)
        self._zoom_level = 1.0
        self._update_scroll_region()

    def _update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all") or (0, 0, 500, 400))

    def clear(self):
        """Limpia el canvas."""
        self._show_placeholder()
