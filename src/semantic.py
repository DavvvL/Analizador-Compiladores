"""
semantic.py — Analizador Semántico.

Recorre el AST y realiza validaciones lógicas:
  - Variables declaradas antes de uso
  - Comprobación básica de tipos en operaciones
  - Funciones definidas antes de llamadas
"""

from .ast_nodes import (
    ASTNode, ProgramNode, AssignNode, FunctionDefNode, IfNode, WhileNode,
    ReturnNode, PrintNode, ExprStmtNode, BinOpNode, UnaryOpNode,
    ComparisonNode, BoolOpNode, NotNode, NumberNode, FloatNode,
    StringNode, BoolNode, NoneNode, IdentifierNode, FunctionCallNode,
    ListNode, ElifNode, ElseNode, ConditionWrapper, ParamsNode, ForNode,
)


# ── Tipos inferidos ──────────────────────────────────────────────────────

TYPE_INT = "int"
TYPE_FLOAT = "float"
TYPE_STRING = "str"
TYPE_BOOL = "bool"
TYPE_NONE = "None"
TYPE_LIST = "list"
TYPE_UNKNOWN = "desconocido"

# Tipos numéricos compatibles entre sí
NUMERIC_TYPES = {TYPE_INT, TYPE_FLOAT}


# ── Scope (tabla de símbolos) ────────────────────────────────────────────

class Scope:
    """Tabla de símbolos con soporte para scopes anidados."""

    def __init__(self, parent=None, name="global"):
        self.parent = parent
        self.name = name
        self.symbols: dict[str, str] = {}  # nombre -> tipo

    def define(self, name: str, type_: str):
        """Define una variable en el scope actual."""
        self.symbols[name] = type_

    def lookup(self, name: str) -> str | None:
        """Busca una variable en este scope y sus padres."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def is_defined(self, name: str) -> bool:
        """Verifica si una variable está definida."""
        return self.lookup(name) is not None


# ── Analizador Semántico ─────────────────────────────────────────────────

class SemanticAnalyzer:
    """
    Recorre el AST con visitor pattern y reporta errores semánticos.

    Validaciones:
    1. Variable usada sin declarar/asignar
    2. Incompatibilidad de tipos en operaciones aritméticas
    3. Función no definida antes de su uso
    """

    def __init__(self):
        self.errors: list[str] = []
        self.scope = Scope()
        # Registro de funciones definidas: name -> (param_count, param_names)
        self.functions: dict[str, tuple[int, list[str]]] = {}
        # Funciones built-in
        self.builtins = {'print', 'len', 'range', 'int', 'float', 'str', 'input', 'type', 'abs'}

    def analyze(self, ast: ASTNode) -> list[str]:
        """Punto de entrada: analiza el AST completo."""
        self.errors = []
        self.scope = Scope()
        self.functions = {}

        if ast is None:
            self.errors.append("No se puede realizar análisis semántico: AST vacío")
            return self.errors

        self._visit(ast)
        return self.errors

    def _error(self, lineno: int, msg: str):
        self.errors.append(f"[Línea {lineno}] Error semántico: {msg}")

    def _warning(self, lineno: int, msg: str):
        self.errors.append(f"[Línea {lineno}] Advertencia: {msg}")

    # ── Visitor dispatch ─────────────────────────────────────────────────

    def _visit(self, node: ASTNode) -> str:
        """Despacha al método visitor correcto según el tipo de nodo."""
        method_name = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self._visit_generic)
        return visitor(node)

    def _visit_generic(self, node: ASTNode) -> str:
        """Visitor por defecto: recorre hijos."""
        for child in node.children():
            if child is not None:
                self._visit(child)
        return TYPE_UNKNOWN

    # ── Programa ─────────────────────────────────────────────────────────

    def _visit_ProgramNode(self, node: ProgramNode) -> str:
        # Primera pasada: registrar funciones (para permitir llamadas adelantadas)
        for stmt in node.statements:
            if isinstance(stmt, FunctionDefNode):
                self.functions[stmt.name] = (len(stmt.params), stmt.params)
                self.scope.define(stmt.name, "function")

        # Segunda pasada: analizar todo
        for stmt in node.statements:
            self._visit(stmt)
        return TYPE_NONE

    # ── Asignación ───────────────────────────────────────────────────────

    def _visit_AssignNode(self, node: AssignNode) -> str:
        value_type = self._visit(node.value)
        self.scope.define(node.name, value_type)
        return value_type

    # ── Función ──────────────────────────────────────────────────────────

    def _visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        # Crear nuevo scope para la función
        func_scope = Scope(parent=self.scope, name=f"función '{node.name}'")
        old_scope = self.scope
        self.scope = func_scope

        # Agregar parámetros al scope
        for param in node.params:
            self.scope.define(param, TYPE_UNKNOWN)

        # Analizar cuerpo
        for stmt in node.body:
            self._visit(stmt)

        # Restaurar scope
        self.scope = old_scope
        return TYPE_NONE

    # ── If ───────────────────────────────────────────────────────────────

    def _visit_IfNode(self, node: IfNode) -> str:
        self._visit(node.condition)
        for stmt in node.body:
            self._visit(stmt)
        for cond, body in node.elif_clauses:
            self._visit(cond)
            for stmt in body:
                self._visit(stmt)
        for stmt in node.else_body:
            self._visit(stmt)
        return TYPE_NONE

    # ── While ────────────────────────────────────────────────────────────

    def _visit_WhileNode(self, node: WhileNode) -> str:
        self._visit(node.condition)
        for stmt in node.body:
            self._visit(stmt)
        return TYPE_NONE

    # ── Return ───────────────────────────────────────────────────────────

    def _visit_ReturnNode(self, node: ReturnNode) -> str:
        if node.value:
            return self._visit(node.value)
        return TYPE_NONE

    # ── Print ────────────────────────────────────────────────────────────

    def _visit_PrintNode(self, node: PrintNode) -> str:
        for arg in node.args:
            self._visit(arg)
        return TYPE_NONE

    # ── Expresión como sentencia ─────────────────────────────────────────

    def _visit_ExprStmtNode(self, node: ExprStmtNode) -> str:
        if node.expr:
            return self._visit(node.expr)
        return TYPE_NONE

    # ── Operación binaria ────────────────────────────────────────────────

    def _visit_BinOpNode(self, node: BinOpNode) -> str:
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        # Verificación de compatibilidad de tipos
        if left_type != TYPE_UNKNOWN and right_type != TYPE_UNKNOWN:
            if node.op == '+':
                # Concatenación de strings es válida
                if left_type == TYPE_STRING and right_type == TYPE_STRING:
                    return TYPE_STRING
                # Suma numérica
                if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                    return TYPE_FLOAT if TYPE_FLOAT in (left_type, right_type) else TYPE_INT
                # Mezcla inválida
                if left_type == TYPE_STRING or right_type == TYPE_STRING:
                    self._error(
                        node.lineno,
                        f"No se puede operar '{node.op}' entre tipos "
                        f"'{left_type}' y '{right_type}'"
                    )
                    return TYPE_UNKNOWN
            elif node.op in ('-', '*', '/'):
                if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                    if node.op == '/':
                        return TYPE_FLOAT
                    return TYPE_FLOAT if TYPE_FLOAT in (left_type, right_type) else TYPE_INT
                if left_type == TYPE_STRING or right_type == TYPE_STRING:
                    self._error(
                        node.lineno,
                        f"No se puede operar '{node.op}' entre tipos "
                        f"'{left_type}' y '{right_type}'"
                    )
                    return TYPE_UNKNOWN

        # Si alguno es desconocido, retornamos desconocido
        if left_type in NUMERIC_TYPES or right_type in NUMERIC_TYPES:
            return TYPE_FLOAT if TYPE_FLOAT in (left_type, right_type) else TYPE_INT
        return TYPE_UNKNOWN

    # ── Operación unaria ─────────────────────────────────────────────────

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand_type = self._visit(node.operand)
        if operand_type == TYPE_STRING:
            self._error(node.lineno, f"Operador unario '{node.op}' no aplicable a tipo 'str'")
        return operand_type

    # ── Comparación ──────────────────────────────────────────────────────

    def _visit_ComparisonNode(self, node: ComparisonNode) -> str:
        self._visit(node.left)
        self._visit(node.right)
        return TYPE_BOOL

    # ── Operación booleana ───────────────────────────────────────────────

    def _visit_BoolOpNode(self, node: BoolOpNode) -> str:
        self._visit(node.left)
        self._visit(node.right)
        return TYPE_BOOL

    # ── Not ──────────────────────────────────────────────────────────────

    def _visit_NotNode(self, node: NotNode) -> str:
        self._visit(node.operand)
        return TYPE_BOOL

    # ── Literales ────────────────────────────────────────────────────────

    def _visit_NumberNode(self, node: NumberNode) -> str:
        return TYPE_INT

    def _visit_FloatNode(self, node: FloatNode) -> str:
        return TYPE_FLOAT

    def _visit_StringNode(self, node: StringNode) -> str:
        return TYPE_STRING

    def _visit_BoolNode(self, node: BoolNode) -> str:
        return TYPE_BOOL

    def _visit_NoneNode(self, node: NoneNode) -> str:
        return TYPE_NONE

    # ── Identificador ────────────────────────────────────────────────────

    def _visit_IdentifierNode(self, node: IdentifierNode) -> str:
        var_type = self.scope.lookup(node.name)
        if var_type is None:
            # No es una variable ni una función conocida
            if node.name not in self.functions and node.name not in self.builtins:
                self._error(
                    node.lineno,
                    f"Variable '{node.name}' usada sin haber sido declarada/asignada"
                )
            return TYPE_UNKNOWN
        return var_type

    # ── Llamada a función ────────────────────────────────────────────────

    def _visit_FunctionCallNode(self, node: FunctionCallNode) -> str:
        # Verificar que la función existe
        if node.name not in self.functions and node.name not in self.builtins:
            self._error(
                node.lineno,
                f"Función '{node.name}' no definida"
            )
        elif node.name in self.functions:
            expected_params, _ = self.functions[node.name]
            if len(node.args) != expected_params:
                self._error(
                    node.lineno,
                    f"Función '{node.name}' espera {expected_params} "
                    f"argumento(s), pero recibió {len(node.args)}"
                )

        # Analizar argumentos
        for arg in node.args:
            self._visit(arg)

        return TYPE_UNKNOWN

    # ── Lista ────────────────────────────────────────────────────────────

    def _visit_ListNode(self, node: ListNode) -> str:
        for elem in node.elements:
            self._visit(elem)
        return TYPE_LIST


# ══════════════════════════════════════════════════════════════════════════
# API PÚBLICA
# ══════════════════════════════════════════════════════════════════════════

def analyze_semantics(ast: ASTNode) -> list[str]:
    """
    Realiza el análisis semántico sobre el AST.

    Returns:
        list[str]: Lista de errores/advertencias semánticas.
                   Lista vacía = análisis exitoso.
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)
