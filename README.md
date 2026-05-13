# Analizador de Python — Léxico · Sintáctico · Semántico

Aplicación de escritorio desarrollada en Python que realiza los tres tipos de análisis de compiladores sobre código fuente estilo Python: **análisis léxico**, **análisis sintáctico** y **análisis semántico**, con una interfaz gráfica moderna y oscura.

---

## Características

- **Análisis Léxico** — Tokeniza el código fuente e identifica cada elemento: palabras reservadas, identificadores, literales, operadores y símbolos de puntuación.
- **Análisis Sintáctico** — Construye y visualiza el **Árbol de Sintaxis Abstracta (AST)** usando un parser LALR basado en PLY, con soporte para indentación estilo Python.
- **Análisis Semántico** — Detecta errores como variables no declaradas, funciones no definidas y tipos incompatibles.
-  **Interfaz moderna** — Tema oscuro con CustomTkinter, editor con numeración de líneas, panel ajustable y tabla de tokens interactiva.
-  **Carga de archivos** — Soporte para abrir archivos `.py` directamente desde la aplicación.

---

## Estructura del proyecto

```
python_analyzer_v2/
├── src/
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── lexer.py            # Analizador léxico (PLY) + preprocesador de indentación
│   ├── parser_module.py    # Parser LALR (PLY) + construcción del AST
│   ├── ast_nodes.py        # Definición de nodos del AST
│   ├── semantic.py         # Análisis semántico (tabla de símbolos)
│   └── ui/
│       ├── app.py          # Ventana principal y orquestador
│       ├── editor.py       # Editor de código con número de líneas
│       ├── token_table.py  # Tabla de tokens (pestaña Léxico)
│       ├── ast_canvas.py   # Visualizador del AST en canvas (pestaña Sintáctico)
│       └── console.py      # Consola de resultados (pestaña Semántico)
├── examples/
│   └── sample.py           # Código de ejemplo para probar el analizador
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución

### Requisitos previos

- Python 3.10 o superior
- pip

### 1. Clona el repositorio

```bash
git clone https://github.com/DavvvL/Analizador-Compiladores.git
cd Analizador-Compiladores
```

### 2. Crea y activa un entorno virtual (recomendado)

```bash
python -m venv venv

# En macOS / Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecuta la aplicación

```bash
python src/main.py
```

---

## Dependencias

| Librería | Versión mínima | Uso |
|---|---|---|
| `customtkinter` | ≥ 5.2.0 | Interfaz gráfica moderna con tema oscuro |
| `ply` | ≥ 3.11 | Lexer y parser LALR (Python Lex-Yacc) |
| `Pillow` | ≥ 10.0.0 | Soporte de imágenes en la interfaz |

---

## Tokens reconocidos

| Categoría | Elementos |
|---|---|
| **Palabras reservadas** | `def`, `if`, `elif`, `else`, `while`, `for`, `in`, `return`, `print`, `and`, `or`, `not`, `True`, `False`, `None` |
| **Literales** | Enteros, flotantes, cadenas (comillas simples y dobles) |
| **Operadores aritméticos** | `+`, `-`, `*`, `/` |
| **Operadores de comparación** | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| **Asignación** | `=` |
| **Puntuación** | `:`, `(`, `)`, `,`, `[`, `]` |
| **Indentación** | `INDENT`, `DEDENT`, `NEWLINE` (generados automáticamente) |

---

## 🌳 Construcciones sintácticas soportadas

- Asignación de variables: `x = 10`
- Definición de funciones: `def nombre(params):`
- Condicionales: `if / elif / else`
- Bucles: `while`, `for ... in`
- Llamadas a funciones: `suma(a, b)`
- `print(...)` y `return`
- Expresiones aritméticas y de comparación



Este proyecto es de uso académico y educativo.
