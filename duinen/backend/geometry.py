from __future__ import annotations
import enum
from math import sqrt

class Direction(enum.Enum):
    East = 0
    North = 1
    West = 2
    South = 3

class Slope:
    class Quadrant(enum.Enum):
        First = 1
        Second = 2
        Third = 3
        Fourth = 4
        East = -1
        North = -2
        West = -3
        South = -4

    def __init__(self, rocy : float, rocx : float):
        if(rocx == 0 and rocy == 0):
            raise ValueError("Slope can't be a point.")
        self.rocy = rocy
        self.rocx = rocx

    def get_quadrant(self) -> int:
        if(self.rocx == 0):
            if(self.rocy > 0):
                return Slope.Quadrant.North
            elif(self.rocy < 0):
                return Slope.Quadrant.South
            else:
                raise AttributeError()
        elif(self.rocy == 0):
            if(self.rocx > 0):
                return Slope.Quadrant.East
            elif(self.rocx < 0):
                return Slope.Quadrant.West
            else:
                raise AttributeError()
        elif(self.rocy > 0 and self.rocx > 0):
            return Slope.Quadrant.First
        elif(self.rocy > 0 and self.rocx < 0):
            return Slope.Quadrant.Second
        elif(self.rocy < 0 and self.rocx < 0):
            return Slope.Quadrant.Third
        elif(self.rocy < 0 and self.rocx > 0):
            return Slope.Quadrant.Fourth
        else:
            AssertionError("Implementation fault in Slope.get_quadrant: indecisive")

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