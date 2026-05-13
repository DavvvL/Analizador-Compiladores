"""
parser_module.py — Analizador Sintáctico basado en PLY YACC.

Define una gramática libre de contexto para un subconjunto de Python
y construye un Árbol de Sintaxis Abstracta (AST) durante el análisis.
"""

import ply.yacc as yacc
import sys
import os

# Importar tokens del lexer (requerido por PLY)
from .lexer import tokens, get_token_stream
from .ast_nodes import (
    ProgramNode, AssignNode, FunctionDefNode, IfNode, WhileNode,
    ReturnNode, PrintNode, ExprStmtNode, BinOpNode, UnaryOpNode,
    ComparisonNode, BoolOpNode, NotNode, NumberNode, FloatNode,
    StringNode, BoolNode, NoneNode, IdentifierNode, FunctionCallNode,
    ListNode,
)


# ── Lista de errores ─────────────────────────────────────────────────────

_parse_errors = []


def _error(msg):
    _parse_errors.append(msg)


# ── Precedencia de operadores ────────────────────────────────────────────

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS', 'UPLUS'),
)


# ══════════════════════════════════════════════════════════════════════════
# REGLAS GRAMATICALES
# ══════════════════════════════════════════════════════════════════════════

# ── Programa ─────────────────────────────────────────────────────────────

def p_program(p):
    """program : statement_list"""
    p[0] = ProgramNode(statements=p[1], lineno=1)


def p_statement_list_multi(p):
    """statement_list : statement_list statement"""
    p[0] = p[1] + [p[2]]


def p_statement_list_single(p):
    """statement_list : statement"""
    p[0] = [p[1]]


# ── Sentencias ───────────────────────────────────────────────────────────

def p_statement(p):
    """statement : assignment_stmt
                 | func_def_stmt
                 | if_stmt
                 | while_stmt
                 | return_stmt
                 | print_stmt
                 | expr_stmt"""
    p[0] = p[1]


# ── Asignación ───────────────────────────────────────────────────────────

def p_assignment_stmt(p):
    """assignment_stmt : IDENTIFIER ASSIGN expression NEWLINE"""
    p[0] = AssignNode(name=p[1], value=p[3], lineno=p.lineno(1))


# ── Definición de función ────────────────────────────────────────────────

def p_func_def_stmt(p):
    """func_def_stmt : DEF IDENTIFIER LPAREN param_list RPAREN COLON NEWLINE block"""
    p[0] = FunctionDefNode(name=p[2], params=p[4], body=p[8], lineno=p.lineno(1))


def p_func_def_stmt_no_params(p):
    """func_def_stmt : DEF IDENTIFIER LPAREN RPAREN COLON NEWLINE block"""
    p[0] = FunctionDefNode(name=p[2], params=[], body=p[7], lineno=p.lineno(1))


def p_param_list_multi(p):
    """param_list : param_list COMMA IDENTIFIER"""
    p[0] = p[1] + [p[3]]


def p_param_list_single(p):
    """param_list : IDENTIFIER"""
    p[0] = [p[1]]


# ── Bloque indentado ────────────────────────────────────────────────────

def p_block(p):
    """block : INDENT statement_list DEDENT"""
    p[0] = p[2]


# ── If / Elif / Else ────────────────────────────────────────────────────

def p_if_stmt(p):
    """if_stmt : IF expression COLON NEWLINE block elif_list else_clause"""
    p[0] = IfNode(
        condition=p[2], body=p[5],
        elif_clauses=p[6], else_body=p[7],
        lineno=p.lineno(1)
    )


def p_if_stmt_no_else(p):
    """if_stmt : IF expression COLON NEWLINE block elif_list"""
    p[0] = IfNode(
        condition=p[2], body=p[5],
        elif_clauses=p[6], else_body=[],
        lineno=p.lineno(1)
    )


def p_elif_list_multi(p):
    """elif_list : elif_list elif_clause"""
    p[0] = p[1] + [p[2]]


def p_elif_list_empty(p):
    """elif_list : """
    p[0] = []


def p_elif_clause(p):
    """elif_clause : ELIF expression COLON NEWLINE block"""
    p[0] = (p[2], p[5])


def p_else_clause(p):
    """else_clause : ELSE COLON NEWLINE block"""
    p[0] = p[4]


# ── While ────────────────────────────────────────────────────────────────

def p_while_stmt(p):
    """while_stmt : WHILE expression COLON NEWLINE block"""
    p[0] = WhileNode(condition=p[2], body=p[5], lineno=p.lineno(1))


# ── Return ───────────────────────────────────────────────────────────────

def p_return_stmt_expr(p):
    """return_stmt : RETURN expression NEWLINE"""
    p[0] = ReturnNode(value=p[2], lineno=p.lineno(1))


def p_return_stmt_empty(p):
    """return_stmt : RETURN NEWLINE"""
    p[0] = ReturnNode(value=None, lineno=p.lineno(1))


# ── Print ────────────────────────────────────────────────────────────────

def p_print_stmt(p):
    """print_stmt : PRINT LPAREN arg_list RPAREN NEWLINE"""
    p[0] = PrintNode(args=p[3], lineno=p.lineno(1))


def p_print_stmt_empty(p):
    """print_stmt : PRINT LPAREN RPAREN NEWLINE"""
    p[0] = PrintNode(args=[], lineno=p.lineno(1))


# ── Expresión como sentencia ─────────────────────────────────────────────

def p_expr_stmt(p):
    """expr_stmt : expression NEWLINE"""
    p[0] = ExprStmtNode(expr=p[1], lineno=p.lineno(1))


# ── Lista de argumentos ─────────────────────────────────────────────────

def p_arg_list_multi(p):
    """arg_list : arg_list COMMA expression"""
    p[0] = p[1] + [p[3]]


def p_arg_list_single(p):
    """arg_list : expression"""
    p[0] = [p[1]]


# ══════════════════════════════════════════════════════════════════════════
# EXPRESIONES
# ══════════════════════════════════════════════════════════════════════════

# ── Expresión OR ─────────────────────────────────────────────────────────

def p_expression_or(p):
    """expression : expression OR expression"""
    p[0] = BoolOpNode(op='or', left=p[1], right=p[3], lineno=p.lineno(2))


# ── Expresión AND ────────────────────────────────────────────────────────

def p_expression_and(p):
    """expression : expression AND expression"""
    p[0] = BoolOpNode(op='and', left=p[1], right=p[3], lineno=p.lineno(2))


# ── Expresión NOT ────────────────────────────────────────────────────────

def p_expression_not(p):
    """expression : NOT expression"""
    p[0] = NotNode(operand=p[2], lineno=p.lineno(1))


# ── Comparaciones ───────────────────────────────────────────────────────

def p_expression_comparison(p):
    """expression : expression EQ expression
                  | expression NEQ expression
                  | expression GT expression
                  | expression LT expression
                  | expression GTE expression
                  | expression LTE expression"""
    p[0] = ComparisonNode(op=p[2], left=p[1], right=p[3], lineno=p.lineno(2))


# ── Aritmética ──────────────────────────────────────────────────────────

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression"""
    p[0] = BinOpNode(op=p[2], left=p[1], right=p[3], lineno=p.lineno(2))


# ── Unarios ──────────────────────────────────────────────────────────────

def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = UnaryOpNode(op='-', operand=p[2], lineno=p.lineno(1))


def p_expression_uplus(p):
    """expression : PLUS expression %prec UPLUS"""
    p[0] = UnaryOpNode(op='+', operand=p[2], lineno=p.lineno(1))


# ── Llamada a función ───────────────────────────────────────────────────

def p_expression_func_call(p):
    """expression : IDENTIFIER LPAREN arg_list RPAREN"""
    p[0] = FunctionCallNode(name=p[1], args=p[3], lineno=p.lineno(1))


def p_expression_func_call_empty(p):
    """expression : IDENTIFIER LPAREN RPAREN"""
    p[0] = FunctionCallNode(name=p[1], args=[], lineno=p.lineno(1))


# ── Agrupación ──────────────────────────────────────────────────────────

def p_expression_paren(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


# ── Lista literal ───────────────────────────────────────────────────────

def p_expression_list(p):
    """expression : LBRACKET arg_list RBRACKET"""
    p[0] = ListNode(elements=p[2], lineno=p.lineno(1))


def p_expression_list_empty(p):
    """expression : LBRACKET RBRACKET"""
    p[0] = ListNode(elements=[], lineno=p.lineno(1))


# ── Átomos ───────────────────────────────────────────────────────────────

def p_expression_integer(p):
    """expression : INTEGER"""
    p[0] = NumberNode(value=p[1], lineno=p.lineno(1))


def p_expression_float(p):
    """expression : FLOAT"""
    p[0] = FloatNode(value=p[1], lineno=p.lineno(1))


def p_expression_string(p):
    """expression : STRING"""
    p[0] = StringNode(value=p[1], lineno=p.lineno(1))


def p_expression_true(p):
    """expression : TRUE"""
    p[0] = BoolNode(value=True, lineno=p.lineno(1))


def p_expression_false(p):
    """expression : FALSE"""
    p[0] = BoolNode(value=False, lineno=p.lineno(1))


def p_expression_none(p):
    """expression : NONE"""
    p[0] = NoneNode(lineno=p.lineno(1))


def p_expression_identifier(p):
    """expression : IDENTIFIER"""
    p[0] = IdentifierNode(name=p[1], lineno=p.lineno(1))


# ── Manejo de errores ───────────────────────────────────────────────────

def p_error(p):
    if p:
        _error(f"Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})")
    else:
        _error("Error de sintaxis: fin de archivo inesperado")


# ══════════════════════════════════════════════════════════════════════════
# API PÚBLICA
# ══════════════════════════════════════════════════════════════════════════

def parse(source: str):
    """
    Analiza el código fuente y retorna (ast, errores).

    Returns:
        tuple: (ProgramNode o None, list[str] de errores)
    """
    global _parse_errors
    _parse_errors = []

    # Redirigir stderr para capturar warnings de PLY
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')

    try:
        parser = yacc.yacc(debug=False, write_tables=False)
        token_stream = get_token_stream(source)
        result = parser.parse(lexer=token_stream, tracking=True)
    except Exception as e:
        _error(f"Error durante el análisis sintáctico: {str(e)}")
        result = None
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr

    return result, list(_parse_errors)
