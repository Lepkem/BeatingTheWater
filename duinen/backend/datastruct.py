import enum
from math import sqrt
from typing import Tuple
from __future__ import annotations

class Rating(enum.Enum):
    Weak = 0
    StrongNoOverlap = 1
    Strong = 2

class Direction(enum.Enum):
    East = 0
    North = 1
    West = 2
    South = 3

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

class Node:
    threshold = None
    def __init__(self, x_min : float, x_max : float, y_min : float, y_max : float, height : float):
        if(self.threshold is None):
            raise AttributeError("Can't process the image, because the threshold is not set.")
        if(x_min >= x_max or y_min >= y_max):
            raise ValueError("Invalid boundaries")

        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

        self._west = None
        self._north = None
        self._east = None
        self._south = None

        self._rating = Rating.Strong if (height >= self.threshold) else Rating.Weak
        self.subscribers = list()
        self._notify = None

    def _downgrade_rating(self):
        if self._rating == 2:
            self._rating = Rating.StrongNoOverlap

    def _notify_factory(self, this_route_id : int) -> function:
        def notify(route_id : int, rating : int):
            if this_route_id != route_id and rating == Rating.Weak:
                self._downgrade_rating()
        return notify
    
    def notify(self, route_id : int):
        if(self._rating == Rating.Weak):
            for callback in self.subscribers:
                callback(route_id, self._rating)

    def link_neighbor(self, neighbor: Node, direction : int):
        def err():
            raise AttributeError("One or both of the nodes is/are already linked to another node.")
        if(direction == Direction.East):
            if(self._east is not None or neighbor._west is not None):
                err()
            self._east = neighbor
            neighbor._west = self
        elif(direction == Direction.North):
            if(self._north is not None or neighbor._south is not None):
                err()
            self._north = neighbor
            neighbor._south = self
        elif(direction == Direction.West):
            if(self._west is not None or neighbor._east is not None):
                err()
            self._west = neighbor
            neighbor._east = self
        elif(direction == Direction.South):
            if(self._south is not None or neighbor._north is not None):
                err()
            self._south = neighbor
            neighbor._north = self
        else:
            raise ValueError("Direction not recognized")

    def curried_link_neighbor(self, neighbor, direction : int):
        self.link_neighbor(neighbor, direction)
        return self

    def _is_within(self, point : Point) -> bool:
        if(point.x < self._x_min or point.x > self._x_max):
            return False
        if(point.y < self._y_min or point.y > self._y_max):
            return False
        return True

    def _calculate_out(self, entry : Point, slope : float) -> Tuple[Point, Node]:
        raise NotImplementedError()

    def _subscribe_neighbors(self):
        if(self._notify is None):
            raise AttributeError("Notify callback function is not defined.")
        
        northeast, northwest, southwest, southeast = False
        def subscribe(target : Node):
            target.subscribers.append(self._notify)

        if(self._east is not None):
            subscribe(self._east)
            if(not northeast and self._east._north is not None):
                subscribe(self._east._north)
                northeast = True
            if(not southeast and self._east._south is not None):
                subscribe(self._east._south)
                southeast = True
        if(self._north is not None):
            subscribe(self._north)
            if(not northeast and self._north._east is not None):
                subscribe(self._north._east)
                northeast = True
            if(not northwest and self._north._west is not None):
                subscribe(self._north._west)
                northwest = True
        if(self._west is not None):
            subscribe(self._west)
            if(not northwest and self._west._north is not None):
                subscribe(self._west._north)
                northwest = True
            if(not southwest and self._west._south is not None):
                subscribe(self._west._south)
                southwest = True
        if(self._south is not None):
            subscribe(self._south)
            if(not southwest and self._south._west is not None):
                subscribe(self._south._west)
                southwest = True
            if(not southeast and self._south._east is not None):
                subscribe(self._south._east)
                southeast = True

    def route(self, entry : Point, slope : float, route_id : int) -> Tuple[Node, Point, float]:
        if(not self._is_within(entry)):
            raise ValueError("Entry point out of boundary.")
        self._notify = self._notify_factory(route_id)
        if(self._rating == Rating.Strong):
            self._subscribe_neighbors()
        out, next = self._calculate_out(entry, slope)
        distance = entry.distance(out) if self._rating != Rating.Weak else 0
        return next, out, distance

