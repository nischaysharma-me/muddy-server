"""Calculator tool for safe math evaluation."""

import math
from app.tools.registry import registry


@registry.register(
    name="calculator",
    description="Evaluates a mathematical expression safely. Example inputs: '2 + 2', 'math.sqrt(144)', '25 * 4'.",
    category="math",
)
def calculate(expression: str) -> str:
    """Safely evaluates a mathematical expression and returns the result as string."""
    allowed_names = {
        "math": math,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "pi": math.pi,
        "e": math.e,
    }

    try:
        # Strip dangerous builtins
        clean_expr = expression.strip()
        result = eval(clean_expr, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"
