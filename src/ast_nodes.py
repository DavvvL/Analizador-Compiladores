"""
ast_nodes.py — Definiciones de nodos del Árbol de Sintaxis Abstracta (AST).

Cada nodo representa una construcción del lenguaje y almacena
el número de línea para mensajes de error detallados.
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Base ─────────────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    """Nodo base del AST."""
    lineno: int = 0

    def children(self) -> list:
        """Retorna los nodos hijos para recorrido del árbol."""
        return []

    def label(self) -> str:
        """Etiqueta para visualización."""
        return self.__class__.__name__


# ── Programa ─────────────────────────────────────────────────────────────

@dataclass
class ProgramNode(ASTNode):
    """Nodo raíz: contiene una lista de sentencias."""
    statements: list = field(default_factory=list)

    def children(self):
        return self.statements

    def label(self):
        return "Programa"


# ── Sentencias ───────────────────────────────────────────────────────────

@dataclass
class AssignNode(ASTNode):
    """Asignación: identificador = expresión."""
    name: str = ""
    value: Optional[ASTNode] = None

    def children(self):
        return [self.value] if self.value else []

    def label(self):
        return f"Asignar\n{self.name} ="


@dataclass
class FunctionDefNode(ASTNode):
    """Definición de función: def nombre(params): bloque."""
    name: str = ""
    params: list = field(default_factory=list)
    body: list = field(default_factory=list)

    def children(self):
        nodes = []
        if self.params:
            nodes.append(ParamsNode(params=self.params, lineno=self.lineno))
        nodes.extend(self.body)
        return nodes

    def label(self):
        return f"def {self.name}"


@dataclass
class ParamsNode(ASTNode):
    """Nodo auxiliar para visualizar parámetros."""
    params: list = field(default_factory=list)

    def children(self):
        return []

    def label(self):
        return f"Params: {', '.join(self.params)}"


@dataclass
class IfNode(ASTNode):
    """Sentencia if/elif/else."""
    condition: Optional[ASTNode] = None
    body: list = field(default_factory=list)
    elif_clauses: list = field(default_factory=list)  # list of (condition, body)
    else_body: list = field(default_factory=list)

    def children(self):
        nodes = []
        if self.condition:
            nodes.append(ConditionWrapper(child=self.condition, lineno=self.lineno))
        nodes.extend(self.body)
        for cond, body in self.elif_clauses:
            nodes.append(ElifNode(condition=cond, body=body, lineno=cond.lineno))
        if self.else_body:
            nodes.append(ElseNode(body=self.else_body, lineno=self.lineno))
        return nodes

    def label(self):
        return "if"


@dataclass
class ElifNode(ASTNode):
    """Cláusula elif."""
    condition: Optional[ASTNode] = None
    body: list = field(default_factory=list)

    def children(self):
        nodes = []
        if self.condition:
            nodes.append(ConditionWrapper(child=self.condition, lineno=self.lineno))
        nodes.extend(self.body)
        return nodes

    def label(self):
        return "elif"


@dataclass
class ElseNode(ASTNode):
    """Cláusula else."""
    body: list = field(default_factory=list)

    def children(self):
        return self.body

    def label(self):
        return "else"


@dataclass
class ConditionWrapper(ASTNode):
    """Wrapper para condiciones (para visualización)."""
    child: Optional[ASTNode] = None

    def children(self):
        return [self.child] if self.child else []

    def label(self):
        return "Condición"


@dataclass
class WhileNode(ASTNode):
    """Sentencia while."""
    condition: Optional[ASTNode] = None
    body: list = field(default_factory=list)

    def children(self):
        nodes = []
        if self.condition:
            nodes.append(ConditionWrapper(child=self.condition, lineno=self.lineno))
        nodes.extend(self.body)
        return nodes

    def label(self):
        return "while"


@dataclass
class ForNode(ASTNode):
    """Sentencia for (simplificada)."""
    var: str = ""
    iterable: Optional[ASTNode] = None
    body: list = field(default_factory=list)

    def children(self):
        nodes = []
        if self.iterable:
            nodes.append(self.iterable)
        nodes.extend(self.body)
        return nodes

    def label(self):
        return f"for {self.var} in"


@dataclass
class ReturnNode(ASTNode):
    """Sentencia return."""
    value: Optional[ASTNode] = None

    def children(self):
        return [self.value] if self.value else []

    def label(self):
        return "return"


@dataclass
class PrintNode(ASTNode):
    """Sentencia print(args)."""
    args: list = field(default_factory=list)

    def children(self):
        return self.args

    def label(self):
        return "print"


@dataclass
class ExprStmtNode(ASTNode):
    """Expresión como sentencia (ej. llamada a función)."""
    expr: Optional[ASTNode] = None

    def children(self):
        return [self.expr] if self.expr else []

    def label(self):
        return "ExprStmt"


# ── Expresiones ──────────────────────────────────────────────────────────

@dataclass
class BinOpNode(ASTNode):
    """Operación binaria: left op right."""
    op: str = ""
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None

    def children(self):
        nodes = []
        if self.left:
            nodes.append(self.left)
        if self.right:
            nodes.append(self.right)
        return nodes

    def label(self):
        return f"Op: {self.op}"


@dataclass
class UnaryOpNode(ASTNode):
    """Operación unaria: op operand."""
    op: str = ""
    operand: Optional[ASTNode] = None

    def children(self):
        return [self.operand] if self.operand else []

    def label(self):
        return f"Unary: {self.op}"


@dataclass
class ComparisonNode(ASTNode):
    """Comparación: left op right."""
    op: str = ""
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None

    def children(self):
        nodes = []
        if self.left:
            nodes.append(self.left)
        if self.right:
            nodes.append(self.right)
        return nodes

    def label(self):
        return f"Comp: {self.op}"


@dataclass
class BoolOpNode(ASTNode):
    """Operación booleana: left op right."""
    op: str = ""
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None

    def children(self):
        nodes = []
        if self.left:
            nodes.append(self.left)
        if self.right:
            nodes.append(self.right)
        return nodes

    def label(self):
        return f"Bool: {self.op}"


@dataclass
class NotNode(ASTNode):
    """Negación lógica: not expr."""
    operand: Optional[ASTNode] = None

    def children(self):
        return [self.operand] if self.operand else []

    def label(self):
        return "not"


# ── Átomos ───────────────────────────────────────────────────────────────

@dataclass
class NumberNode(ASTNode):
    """Literal numérico (entero)."""
    value: int = 0

    def label(self):
        return f"Int: {self.value}"


@dataclass
class FloatNode(ASTNode):
    """Literal numérico (flotante)."""
    value: float = 0.0

    def label(self):
        return f"Float: {self.value}"


@dataclass
class StringNode(ASTNode):
    """Literal de cadena."""
    value: str = ""

    def label(self):
        display = self.value
        if len(display) > 15:
            display = display[:12] + "..."
        return f'Str: "{display}"'


@dataclass
class BoolNode(ASTNode):
    """Literal booleano."""
    value: bool = False

    def label(self):
        return f"Bool: {self.value}"


@dataclass
class NoneNode(ASTNode):
    """Literal None."""

    def label(self):
        return "None"


@dataclass
class IdentifierNode(ASTNode):
    """Referencia a variable."""
    name: str = ""

    def label(self):
        return f"Var: {self.name}"


@dataclass
class FunctionCallNode(ASTNode):
    """Llamada a función: nombre(args)."""
    name: str = ""
    args: list = field(default_factory=list)

    def children(self):
        return self.args

    def label(self):
        return f"Llamar: {self.name}()"


@dataclass
class ListNode(ASTNode):
    """Lista literal: [elem1, elem2, ...]."""
    elements: list = field(default_factory=list)

    def children(self):
        return self.elements

    def label(self):
        return "Lista []"
