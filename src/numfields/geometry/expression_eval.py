"""Safe math expression evaluation for parametric curves."""

from __future__ import annotations

import ast
import math
from typing import Any

_ALLOWED_NAMES: dict[str, Any] = {
    "pi": math.pi,
    "e": math.e,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sqrt": math.sqrt,
    "abs": abs,
    "pow": pow,
    "min": min,
    "max": max,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "floor": math.floor,
    "ceil": math.ceil,
    "hypot": math.hypot,
}


class ExpressionError(ValueError):
    pass


def _eval_node(node: ast.AST, variables: dict[str, float]) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ExpressionError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in variables:
            return float(variables[node.id])
        if node.id in _ALLOWED_NAMES:
            val = _ALLOWED_NAMES[node.id]
            if isinstance(val, (int, float)):
                return float(val)
        raise ExpressionError(f"Unknown name: {node.id}")
    if isinstance(node, ast.UnaryOp):
        val = _eval_node(node.operand, variables)
        if isinstance(node.op, ast.UAdd):
            return val
        if isinstance(node.op, ast.USub):
            return -val
        raise ExpressionError("Unsupported unary operator")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, variables)
        right = _eval_node(node.right, variables)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise ExpressionError("Unsupported binary operator")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ExpressionError("Only simple function calls are allowed")
        fn = _ALLOWED_NAMES.get(node.func.id)
        if fn is None or not callable(fn):
            raise ExpressionError(f"Unknown function: {node.func.id}")
        args = [_eval_node(arg, variables) for arg in node.args]
        if node.keywords:
            raise ExpressionError("Keyword arguments are not allowed")
        return float(fn(*args))
    raise ExpressionError(f"Unsupported expression syntax: {type(node).__name__}")


def evaluate_expression(expression: str, variables: dict[str, float]) -> float:
    expr = expression.strip()
    if not expr:
        raise ExpressionError("Expression is empty")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Syntax error: {exc.msg}") from exc
    return _eval_node(tree.body, variables)
