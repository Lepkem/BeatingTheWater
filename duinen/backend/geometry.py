from __future__ import annotations
import enum
from math import sqrt

class Direction(enum.Enum):
    East = 0
    North = 1
    West = 2
    South = 3

class Slope:
    """The directional slope is represented by the increase in the dimension of y respective
    to an increase in the dimension of x of 1, defined as slope; The progression in the x dimension
    defined as x_progression, which is represented as > 0 for increasing progression
    and < 0 for decreasing progression. For vertical slope, slope input must be any number > 0
    for north direction, and any number < 0 for south direction."""
    def __init__(self, slope: float, x_progression: float):
        if(x_progression == 0):
            self.x_progression = x_progression
            self.slope = slope
        else:
            self.slope = slope
            self.x_progression = x_progression

    def dy(self, dx: float) -> float:
        return self.slope*dx

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, other : Point) -> float:
        a = abs(self.x - other.x)
        b = abs(self.y - other.y)
        return sqrt(a**2 + b**2)

    def __eq__(self, other : object) -> bool:
        if(not isinstance(other, Point)):
            return False
        return self.x == other.x and self.y == other.y