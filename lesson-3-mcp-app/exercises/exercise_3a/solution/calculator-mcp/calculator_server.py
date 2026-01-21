import math
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator")

MATH_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "golden_ratio": (1 + math.sqrt(5)) / 2,
    "sqrt_2": math.sqrt(2)
}

# ============================================================================
# TOOLS - Basic Calculator Operations
# ============================================================================

@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return f"{a} + {b} = {result}"

@mcp.tool()
def subtract(a: float, b: float) -> str:
    """Subtract second number from first number.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
    """
    result = a - b
    return f"{a} - {b} = {result}"

@mcp.tool()
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    result = a * b
    return f"{a} × {b} = {result}"

@mcp.tool()
def divide(a: float, b: float) -> str:
    """Divide first number by second number.
    
    Args:
        a: Dividend (number to be divided)
        b: Divisor (number to divide by)
    """
    if b == 0:
        return "Error: Cannot divide by zero"
    result = a / b
    return f"{a} ÷ {b} = {result}"

@mcp.tool()
def power(base: float, exponent: float) -> str:
    """Raise a number to a power.
    
    Args:
        base: The base number
        exponent: The power to raise to
    """
    result = base ** exponent
    return f"{base}^{exponent} = {result}"

@mcp.tool()
def square_root(n: float) -> str:
    """Calculate the square root of a number.
    
    Args:
        n: Number to find square root of
    """
    if n < 0:
        return "Error: Cannot calculate square root of negative number"
    result = math.sqrt(n)
    return f"√{n} = {result}"

@mcp.tool()
def percentage(value: float, total: float) -> str:
    """Calculate what percentage one number is of another.
    
    Args:
        value: The value to calculate percentage for
        total: The total amount (100%)
    """
    if total == 0:
        return "Error: Total cannot be zero"
    result = (value / total) * 100
    return f"{value} is {result}% of {total}"

# ============================================================================
# RESOURCES - Math Constants
# ============================================================================

@mcp.resource("constants://math")
def get_math_constants() -> str:
    """Access common mathematical constants."""
    output = "Mathematical Constants:\n\n"
    for name, value in MATH_CONSTANTS.items():
        output += f"{name}: {value}\n"
    return output

@mcp.resource("constants://pi")
def get_pi() -> str:
    """Get the value of pi (π)."""
    return f"π = {MATH_CONSTANTS['pi']}"

@mcp.resource("constants://e")
def get_e() -> str:
    """Get the value of Euler's number (e)."""
    return f"e = {MATH_CONSTANTS['e']}"

@mcp.resource("constants://golden_ratio")
def get_golden_ratio() -> str:
    """Get the value of Golden Ratio."""
    return f"e = {MATH_CONSTANTS['golden_ratio']}"

# ============================================================================
# PROMPTS - Calculation Assistance
# ============================================================================

@mcp.prompt()
def solve_equation(equation: str) -> str:
    """Help solve a mathematical equation or word problem.
    
    Args:
        equation: The equation or problem description
    """
    return f"""Please help me solve this mathematical problem:

{equation}

Break down the solution step by step and use the calculator tools available to perform the calculations. Show your work clearly."""

@mcp.prompt()
def calculation_help(operation: str) -> str:
    """Get help with how to perform a specific calculation.
    
    Args:
        operation: The type of calculation (e.g., 'percentage', 'factorial', 'power')
    """
    return f"""I need help understanding how to use the calculator for: {operation}

Please explain:
1. What this operation does
2. What inputs are needed
3. An example calculation
4. When this operation is commonly used"""

if __name__ == "__main__":
    mcp.run(transport="streamable-http")