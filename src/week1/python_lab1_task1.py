"""
Task 1 – Simple Function with Arithmetic
----------------------------------------
Write a function `circle_area(radius)` that returns the area of a circle.

    area = π × radius²

Requirements:
- Use `math.pi` from the math module (not 3.14).
- The function RETURNS the full, unrounded float. Rounding to 2 decimals
  happens only when printing in the main block.
- You may assume radius >= 0.

In the main block: ask the user for a radius, convert it to a float,
call circle_area(), and print the result with 2 decimals.

Example run:
    Enter radius: 2
    Area of the circle: 12.57

Examples (these are also used to check your work):
>>> round(circle_area(1), 2)
3.14
>>> round(circle_area(2), 2)
12.57
>>> circle_area(0)
0.0
"""

import math

def circle_area(radius: float) -> float:
    """
    Calculate the area of a circle given its radius.

    >>> circle_area(1.0)
    3.141592653589793
    >>> circle_area(5)
    78.53981633974483
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative.")
    return math.pi * (radius ** 2)

if __name__ == "__main__":
    try:
        r = float(input("Enter radius: "))
        print(f"The area of the circle is: {circle_area(r)}")
    except ValueError as e:
        print(f"Invalid input: {e}")
