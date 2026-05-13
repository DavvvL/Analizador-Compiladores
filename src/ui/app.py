"""
app.py — Ventana principal de la aplicación.

Integra todos los componentes de UI y conecta los módulos de análisis
léxico, sintáctico y semántico con la interfaz gráfica.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .editor import CodeEditor
from .token_table import TokenTable
from .ast_canvas import ASTCanvas
from .console import OutputConsole


class PyAnalyzerApp(ctk.CTk):
    """
    Ventana principal del Python Code Analyzer.

    Layout:
    ┌──────────────────────────────────────────────┐
    │                  Title Bar                    │
    ├───────────────────╫──────────────────────────┤
    │                   ║   Tab: Léxico            │
    │   Code Editor     ║   Tab: Sintáctico (AST)  │
    │   (with lines)    ║   Tab: Semántico         │
    │                   ║  ← sash arrastrable →    │
    ├───────────────────╨──────────────────────────┤
    │            Action Buttons                     │
    └──────────────────────────────────────────────┘
    """

    SAMPLE_CODE = """# Ejemplo de código Python
# Escribe tu código aquí o carga un archivo

x = 10
y = 3.14
nombre = "Hola Mundo"

def suma(a, b):
    resultado = a + b
    return resultado

def es_mayor(x, y):
    if x > y:
        print("x es mayor")
        return True
    else:
        print("y es mayor o igual")
        return False

z = suma(x, 5)
print(z)

while x > 0:
    x = x - 1
"""

    def __init__(self):
        super().__init__()

        # ── Configuración de ventana ─────────────────────────────────────
        self.title("Python_analizer_v2")
        self.geometry("1400x850")
        self.minsize(1000, 600)

        # Tema oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Configurar grid principal ────────────────────────────────────
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Title Bar ───────────────────────────────────────────────────
        self._create_title_bar()

        # ── Main Content ────────────────────────────────────────────────
        self._create_main_content()

        # ── Bottom Bar ──────────────────────────────────────────────────
        self._create_bottom_bar()

        # ── Cargar código de ejemplo ─────────────────────────────────────
        self.editor.set_code(self.SAMPLE_CODE.strip())

    def _create_title_bar(self):
        """Crea la barra de título con el nombre de la app."""
        title_bar = ctk.CTkFrame(self, fg_color="#1e2030", height=55, corner_radius=0)
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.grid_propagate(False)
        title_bar.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            title_bar,
            text="   Analizador de PYTHON",
            font=("Segoe UI", 20, "bold"),
            text_color="#c0caf5",
        )
        title_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        # Subtítulo
        subtitle = ctk.CTkLabel(
            title_bar,
            text="Análisis Léxico · Sintáctico · Semántico",
            font=("Segoe UI", 12),
            text_color="#565f89",
        )
        subtitle.grid(row=0, column=2, padx=20, pady=8, sticky="e")



    def _create_main_content(self):
        """Crea el contenido principal con editor y pestañas, separados por un sash arrastrable."""

        # ── Estilo del sash (divisor arrastrrable) ───────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Dark.TPanedwindow",
            background="#1a1b26",
        )
        style.configure(
            "Dark.Sash",
            sashthickness=6,
            sashrelief="flat",
            background="#33467c",
        )

        # ── Contenedor externo (para padding) ────────────────────────────
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 0))
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ── PanedWindow horizontal ───────────────────────────────────────
        self._paned = tk.PanedWindow(
            outer,
            orient="horizontal",
            sashwidth=6,
            sashrelief="flat",
            sashpad=0,
            bg="#0f111a",          # color del sash
            bd=0,
            relief="flat",
            showhandle=False,
        )
        self._paned.grid(row=0, column=0, sticky="nsew")

        # ── Panel izquierdo: Editor ──────────────────────────────────────
        editor_frame = ctk.CTkFrame(self._paned, fg_color="#1a1b26", corner_radius=10)
        editor_frame.grid_rowconfigure(1, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        # Header del editor
        editor_header = ctk.CTkFrame(editor_frame, fg_color="#1e2030", height=38, corner_radius=0)
        editor_header.grid(row=0, column=0, sticky="ew")
        editor_header.grid_propagate(False)

        ctk.CTkLabel(
            editor_header,
            text="  📝 Editor de Código",
            font=("Segoe UI", 13, "bold"),
            text_color="#c0caf5",
            anchor="w",
        ).pack(side="left", padx=10, pady=5)

        self._file_label = ctk.CTkLabel(
            editor_header,
            text="Sin archivo",
            font=("Segoe UI", 11),
            text_color="#565f89",
        )
        self._file_label.pack(side="right", padx=10, pady=5)

        self.editor = CodeEditor(editor_frame, fg_color="transparent")
        self.editor.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # ── Panel derecho: Pestañas ──────────────────────────────────────
        tabs_frame = ctk.CTkFrame(self._paned, fg_color="#1a1b26", corner_radius=10)
        tabs_frame.grid_rowconfigure(0, weight=1)
        tabs_frame.grid_columnconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(
            tabs_frame,
            fg_color="#1a1b26",
            segmented_button_fg_color="#1e2030",
            segmented_button_selected_color="#33467c",
            segmented_button_selected_hover_color="#3d4f8f",
            segmented_button_unselected_color="#1e2030",
            segmented_button_unselected_hover_color="#24283b",
            corner_radius=8,
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Pestaña 1: Léxico
        tab_lexico = self.tabview.add("📋 Léxico")
        tab_lexico.grid_rowconfigure(0, weight=1)
        tab_lexico.grid_columnconfigure(0, weight=1)

        self.token_table = TokenTable(tab_lexico, fg_color="transparent")
        self.token_table.grid(row=0, column=0, sticky="nsew")

        # Pestaña 2: Sintáctico
        tab_syntax = self.tabview.add("🌳 Sintáctico")
        tab_syntax.grid_rowconfigure(0, weight=1)
        tab_syntax.grid_columnconfigure(0, weight=1)

        self.ast_canvas = ASTCanvas(tab_syntax, fg_color="transparent")
        self.ast_canvas.grid(row=0, column=0, sticky="nsew")

        # Pestaña 3: Semántico
        tab_semantic = self.tabview.add("🖥️ Semántico")
        tab_semantic.grid_rowconfigure(0, weight=1)
        tab_semantic.grid_columnconfigure(0, weight=1)

        self.console = OutputConsole(tab_semantic, fg_color="transparent")
        self.console.grid(row=0, column=0, sticky="nsew")

        # ── Agregar paneles al PanedWindow con tamaños iniciales ─────────
        self._paned.add(editor_frame, minsize=320, stretch="always")
        self._paned.add(tabs_frame,   minsize=380, stretch="always")

        # Posición inicial del sash: 40% editor / 60% resultados
        self.update_idletasks()
        self.after(50, self._set_initial_sash)

    def _set_initial_sash(self):
        """Establece la posición inicial del sash tras el primer render."""
        total_w = self._paned.winfo_width()
        if total_w > 10:
            self._paned.sash_place(0, int(total_w * 0.42), 0)


    def _create_bottom_bar(self):
        """Crea la barra inferior con botones de acción."""
        bottom_bar = ctk.CTkFrame(self, fg_color="#1e2030", height=60, corner_radius=0)
        bottom_bar.grid(row=2, column=0, sticky="ew")
        bottom_bar.grid_propagate(False)

        # Centrar botones
        btn_container = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        btn_container.place(relx=0.5, rely=0.5, anchor="center")

        # ── Botón Analizar ──────────────────────────────────────────────
        self.btn_analyze = ctk.CTkButton(
            btn_container,
            text="▶  Analizar Código",
            command=self._analyze_code,
            width=180,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="#7aa2f7",
            hover_color="#5d7fc7",
            corner_radius=8,
        )
        self.btn_analyze.pack(side="left", padx=8)

        # ── Botón Cargar Archivo ─────────────────────────────────────────
        self.btn_load = ctk.CTkButton(
            btn_container,
            text="📂  Cargar Archivo",
            command=self._load_file,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#33467c",
            hover_color="#3d4f8f",
            corner_radius=8,
        )
        self.btn_load.pack(side="left", padx=8)

        # ── Botón Limpiar ────────────────────────────────────────────────
        self.btn_clear = ctk.CTkButton(
            btn_container,
            text="🗑  Limpiar Todo",
            command=self._clear_all,
            width=150,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#33467c",
            hover_color="#3d4f8f",
            corner_radius=8,
        )
        self.btn_clear.pack(side="left", padx=8)

        # ── Status bar ──────────────────────────────────────────────────
        self._status_label = ctk.CTkLabel(
            bottom_bar,
            text="Listo",
            font=("Segoe UI", 11),
            text_color="#565f89",
        )
        self._status_label.place(relx=0.98, rely=0.5, anchor="e")

    # ══════════════════════════════════════════════════════════════════════
    # ACCIONES
    # ══════════════════════════════════════════════════════════════════════

    def _analyze_code(self):
        """Ejecuta los tres análisis: léxico, sintáctico y semántico."""
        code = self.editor.get_code().strip()

        if not code:
            messagebox.showwarning(
                "Sin código",
                "Por favor, escribe o carga código fuente para analizar."
            )
            return

        self._status_label.configure(text="Analizando...")
        self.update_idletasks()

        # Limpiar resultados anteriores
        self.console.clear()

        try:
            # ── 1. Análisis Léxico ───────────────────────────────────────
            from ..lexer import tokenize
            tokens_list = tokenize(code)
            self.token_table.populate(tokens_list)
            self.console.show_lexer_results(len(tokens_list))

            # ── 2. Análisis Sintáctico ───────────────────────────────────
            from ..parser_module import parse
            ast, syntax_errors = parse(code)
            self.console.show_syntax_results(syntax_errors)

            if ast and not syntax_errors:
                self.ast_canvas.draw_ast(ast)
            elif syntax_errors:
                self.ast_canvas.clear()
                self.tabview.set("🖥️ Semántico")
                self._status_label.configure(text="Errores de sintaxis encontrados")
                return

            # ── 3. Análisis Semántico ────────────────────────────────────
            if ast:
                from ..semantic import analyze_semantics
                semantic_errors = analyze_semantics(ast)
                self.console.show_semantic_results(semantic_errors)

                if semantic_errors:
                    self.tabview.set("🖥️ Semántico")
                else:
                    self.tabview.set("📋 Léxico")

            self._status_label.configure(text="Análisis completado ✓")

        except Exception as e:
            self.console.write_error(f"Error inesperado: {str(e)}")
            self._status_label.configure(text="Error durante el análisis")
            self.tabview.set("🖥️ Semántico")
            import traceback
            self.console.write_plain(traceback.format_exc())

    def _load_file(self):
        """Carga un archivo .py en el editor."""
        filepath = filedialog.askopenfilename(
            title="Cargar archivo Python",
            filetypes=[
                ("Archivos Python", "*.py"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.set_code(content)
                filename = os.path.basename(filepath)
                self._file_label.configure(text=f"📄 {filename}")
                self._status_label.configure(text=f"Archivo cargado: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")

    def _clear_all(self):
        """Limpia el editor y todos los resultados."""
        self.editor.clear()
        self.token_table.clear()
        self.ast_canvas.clear()
        self.console.clear()
        self._file_label.configure(text="Sin archivo")
        self._status_label.configure(text="Listo")


