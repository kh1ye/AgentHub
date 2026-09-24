from typing import Literal

from langchain_core.tools import tool


@tool
def calculator(
    a: float,
    b: float,
    operation: Literal["add", "subtract", "multiply", "divide"],
) -> float:
    """Perform one basic arithmetic operation on two numbers."""

    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

