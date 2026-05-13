"""
lexer.py — Analizador Léxico basado en PLY.

Reconoce tokens del lenguaje estilo Python: palabras reservadas,
identificadores, números, cadenas, operadores y puntuación.
"""

import ply.lex as lex


# ── Palabras reservadas ──────────────────────────────────────────────────

RESERVED = {
    'def': 'DEF',
    'if': 'IF',
    'elif': 'ELIF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'return': 'RETURN',
    'print': 'PRINT',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'True': 'TRUE',
    'False': 'FALSE',
    'None': 'NONE',
}

# ── Lista de tokens ─────────────────────────────────────────────────────

tokens = [
    # Literales
    'INTEGER', 'FLOAT', 'STRING',
    # Identificador
    'IDENTIFIER',
    # Operadores aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    # Asignación
    'ASSIGN',
    # Comparación
    'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
    # Puntuación
    'COLON', 'LPAREN', 'RPAREN', 'COMMA',
    'LBRACKET', 'RBRACKET',
    # Indentación (inyectados por el preprocesador)
    'NEWLINE', 'INDENT', 'DEDENT',
] + list(RESERVED.values())


# ── Reglas de tokens simples ─────────────────────────────────────────────

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_COLON = r':'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

# Comparación (orden importa: primero los de 2 chars)
t_EQ = r'=='
t_NEQ = r'!='
t_GTE = r'>='
t_LTE = r'<='
t_GT = r'>'
t_LT = r'<'
t_ASSIGN = r'='


# ── Reglas de tokens complejos ───────────────────────────────────────────

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'(\"([^\\\"]|\\.)*\"|\'([^\\\']|\\.)*\')'
    # Remover las comillas exteriores
    t.value = t.value[1:-1]
    return t


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Verificar si es palabra reservada
    t.type = RESERVED.get(t.value, 'IDENTIFIER')
    return t


# ── Ignorar ──────────────────────────────────────────────────────────────

# Ignorar espacios y tabs dentro de la línea (la indentación se maneja aparte)
t_ignore = ' \t'


def t_COMMENT(t):
    r'\#[^\n]*'
    pass  # Descartar comentarios


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    """Carácter ilegal."""
    t.lexer.skip(1)


# ── Preprocesador de indentación ─────────────────────────────────────────

class IndentToken:
    """Token sintético para INDENT/DEDENT/NEWLINE."""
    def __init__(self, type_, value, lineno):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.lexpos = 0

    def __repr__(self):
        return f"IndentToken({self.type}, {self.value!r}, line={self.lineno})"


def preprocess_indentation(source: str) -> list:
    """
    Preprocesa el código fuente para generar tokens INDENT/DEDENT/NEWLINE.

    Recorre línea por línea, calcula niveles de indentación y genera los
    tokens sintéticos necesarios para que el parser LALR maneje bloques.
    """
    raw_lines = source.split('\n')
    indent_stack = [0]
    processed_tokens = []

    for line_num, raw_line in enumerate(raw_lines, start=1):
        # Ignorar líneas vacías y comentarios puros
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Calcular nivel de indentación (espacios al inicio)
        indent_level = len(raw_line) - len(raw_line.lstrip())

        # Generar INDENT/DEDENT tokens
        if indent_level > indent_stack[-1]:
            indent_stack.append(indent_level)
            processed_tokens.append(IndentToken('INDENT', indent_level, line_num))
        elif indent_level < indent_stack[-1]:
            while indent_stack[-1] > indent_level:
                indent_stack.pop()
                processed_tokens.append(IndentToken('DEDENT', indent_level, line_num))

        # Tokenizar la línea con PLY
        lexer = lex.lex()
        lexer.input(stripped)
        lexer.lineno = line_num
        for tok in lexer:
            tok.lineno = line_num
            processed_tokens.append(tok)

        # Agregar NEWLINE al final de la línea
        processed_tokens.append(IndentToken('NEWLINE', '\\n', line_num))

    # Cerrar bloques abiertos al final del archivo
    while indent_stack[-1] > 0:
        indent_stack.pop()
        processed_tokens.append(IndentToken('DEDENT', 0, line_num if raw_lines else 1))

    return processed_tokens


# ── Clase TokenStream para alimentar al parser ──────────────────────────

class TokenStream:
    """
    Envuelve una lista de tokens preprocesados para que PLY YACC
    pueda consumirlos uno a uno con el método token().
    """
    def __init__(self, token_list):
        self.token_list = token_list
        self.tokens = iter(token_list)
        self.lineno = 1    # PLY YACC requiere este atributo
        self.lexpos = 0    # PLY YACC requiere este atributo para tracking

    def token(self):
        try:
            tok = next(self.tokens)
            self.lineno = getattr(tok, 'lineno', self.lineno)
            self.lexpos = getattr(tok, 'lexpos', self.lexpos)
            return tok
        except StopIteration:
            return None


# ── API pública ──────────────────────────────────────────────────────────

def tokenize(source: str) -> list:
    """
    Tokeniza el código fuente y retorna una lista de diccionarios:
    [{'line': int, 'token': str, 'type': str, 'value': any}, ...]

    Esta función se usa para mostrar la tabla de tokens en la interfaz.
    """
    result = []
    raw_lines = source.split('\n')

    for line_num, raw_line in enumerate(raw_lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        lexer = lex.lex()
        lexer.input(stripped)
        lexer.lineno = line_num

        for tok in lexer:
            result.append({
                'line': line_num,
                'token': str(tok.value),
                'type': tok.type,
                'value': tok.value,
            })

    return result


def get_token_stream(source: str) -> TokenStream:
    """
    Retorna un TokenStream preprocesado listo para el parser PLY.
    Incluye tokens INDENT/DEDENT/NEWLINE.
    """
    token_list = preprocess_indentation(source)
    return TokenStream(token_list)
