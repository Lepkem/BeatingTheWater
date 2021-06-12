from __future__ import annotations
import enum
from math import sqrt
from typing import Tuple
from .. import constants
from qgis.core import *
from . import geometry, utilities, linearregression

class Rating(enum.Enum):
    Weak = 0
    StrongNoOverlap = 1
    Strong = 2

class Node:
    threshold = None
    slope = None
    def __init__(self, x_min : float, x_max : float, y_min : float, y_max : float, height : float):
        if(self.threshold is None):
            raise AttributeError("Can't process the image, because the threshold is not set.")
        if(x_min >= x_max or y_min >= y_max):
            raise ValueError("Invalid boundaries")

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

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
        if(direction == geometry.Direction.East):
            if(self._east is not None or neighbor._west is not None):
                err()
            self._east = neighbor
            neighbor._west = self
        elif(direction == geometry.Direction.North):
            if(self._north is not None or neighbor._south is not None):
                err()
            self._north = neighbor
            neighbor._south = self
        elif(direction == geometry.Direction.West):
            if(self._west is not None or neighbor._east is not None):
                err()
            self._west = neighbor
            neighbor._east = self
        elif(direction == geometry.Direction.South):
            if(self._south is not None or neighbor._north is not None):
                err()
            self._south = neighbor
            neighbor._north = self
        else:
            raise ValueError("Direction not recognized")

    def curried_link_neighbor(self, neighbor: Node, direction : int):
        self.link_neighbor(neighbor, direction)
        return self

    def get_neighbor(self, direction: int) -> Node:
        raise NotImplementedError()

    def _is_within(self, point : geometry.Point) -> bool:
        if(point.x < self.x_min or point.x > self.x_max):
            return False
        if(point.y < self.y_min or point.y > self.y_max):
            return False
        return True

    def _calculate_out(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        quadrant = self.slope.get_quadrant()
        if(quadrant < 0):
            return self._intersect_axis(entry, quadrant)
        elif(quadrant == geometry.Slope.Quadrant.First):
            return self._intersect_first(entry)
        elif(quadrant == geometry.Slope.Quadrant.Second):
            return self._intersect_second(entry)
        elif(quadrant == geometry.Slope.Quadrant.Third):
            return self._intersect_third(entry)
        elif(quadrant == geometry.Slope.Quadrant.Fourth):
            return self._intersect_fourth(entry)
        else:
            raise ValueError("Invalid slope.")


    def _intersect_axis(self, entry : geometry.Point, quadrant : int) -> Tuple[geometry.Point, Node]:
        if(quadrant == geometry.Slope.Quadrant.East):
            return geometry.Point(self.x_max, entry.y), self._east
        elif(quadrant == geometry.Slope.Quadrant.North):
            return geometry.Point(entry.x, self.y_max), self._north
        elif(quadrant == geometry.Slope.Quadrant.West):
            return geometry.Point(self.x_min, entry.y), self._west
        elif(quadrant == geometry.Slope.Quadrant.South):
            return geometry.Point(entry.x, self.y_min), self._south

    def _intersect_first(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_max - entry.x
        dy = self.y_max - entry.y
        dx_derived = dy*self.slope.rocx
        if(dx < dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.rocy), self._east
        elif(dx > dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._north
        else:
            next = self._north._east if self._north is not None and self._north._east is not None else None
            next = self._east._north if self._east is not None and self._east._north is not None else next
            return geometry.Point(self.x_max, self.y_max), next

    def _intersect_second(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_min - entry.x
        dy = self.y_max - entry.y
        dx_derived = dy*self.slope.rocx
        if(dx > dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.rocy), self._west
        elif(dx < dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._north
        else:
            next = self._north._west if self._north is not None and self._north._west is not None else None
            next = self._west._north if self._west is not None and self._west._north is not None else next
            return geometry.Point(self.x_min, self.y_max), next


    def _intersect_third(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_min - entry.x
        dy = self.y_min - entry.y
        dx_derived = dy*self.slope.rocx
        if(dx > dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.rocy), self._west
        elif(dx < dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._south
        else:
            next = self._south._west if self._south is not None and self._south._west is not None else None
            next = self._west._south if self._west is not None and self._west._south is not None else next
            return geometry.Point(self.x_min, self.y_min), next


    def _intersect_fourth(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_max - entry.x
        dy = self.y_min - entry.y
        dx_derived = dy*self.slope.rocx
        if(dx < dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.rocy), self._east
        elif(dx > dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._south
        else:
            next = self._south._east if self._south is not None and self._south._east is not None else None
            next = self._east._south if self._east is not None and self._east._south is not None else next
            return geometry.Point(self.x_max, self.y_min), next

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
    #TODO: replace slope arg by class attr
    def route(self, entry : geometry.Point, slope : float, route_id : int) -> Tuple[Node, geometry.Point, float]:
        if(not self._is_within(entry)):
            raise ValueError("Entry point out of boundary.")
        self._notify = self._notify_factory(route_id)
        if(self._rating == Rating.Strong):
            self._subscribe_neighbors()
        out, next = self._calculate_out(entry, slope)
        distance = entry.distance(out) if self._rating != Rating.Weak else 0
        return next, out, distance

class ImageSingleton:
    class Image:
        resolution = None

        def __init__(self):
            self.x_min = None
            self.x_max = None
            self.y_min = None
            self.y_max = None
            self.northwest = None
            self.northeast = None
            self.southwest = None
            self.southeast = None

            self.cornerdict = dict() #Point to Node
            self._directions = dict() #Node to Tuple[float, float] (x, y) directions

            self.complete = False

        def populate(self, inputfiles: dict, settings: utilities.AlgorithmSettings):
            #set up data stream
            points_input = utilities.csvToDictFunction(inputfiles.get(constants.CSVKEY))
            #determine area to process
            xvals, yvals = linearregression.linreg(points_input)
            start, stop, coast_slope = linearregression.transform_coastline(xvals, yvals)
            Node.slope = linearregression.perpendicular_slope(coast_slope, settings.dune_direction)
            Node.threshold = settings.threshold
            #complete the code above
            #process image pixels into nodes
            data_file = "C:\\Users\\Alexander\\Desktop\\ProjectD_Data\\SpringertduinenAHNhoogdynamisch\\H_2m_2019_Springertduinen.tif"
            #throws a bunch of non-fatal errors
            print("beforeqgis")
            rlayer = QgsRasterLayer(data_file, "H_2m_2019_Springertduinen")
            print("afterqgis")
            #set up navigation dictionaries
            self._finish()

        def seek(self, x: float, y: float) -> Node:
            self._checkComplete()

            def closest(min: float, max: float, value: float) -> Tuple[float, float]:
                mindist = abs(value - min)
                maxdist = abs(max - value)
                return min, mindist if mindist <= maxdist else max, maxdist
            startx, distx = closest(self.x_min, self.x_max, x)
            starty, disty = closest(self.y_min, self.y_max, y)

            curr = self.cornerdict.get(geometry.Point(startx, starty))
            dirx, diry = self._directions.get(curr)
            while distx >= self.resolution:
                curr = curr.get_neighbor(dirx)
                distx -= self.resolution
            while disty >= self.resolution:
                curr = curr.get_neighbor(diry)
                disty -= self.resolution

            return curr
            
        def _checkComplete(self):
            if not self.complete:
                raise AttributeError("Can't read image while processing is not complete.")
        
        def _finish(self):
            self.cornerdict[geometry.Point(self.northeast.x_max, self.northeast.y_max)] = self.northeast
            self.cornerdict[geometry.Point(self.northwest.x_min, self.northwest.y_max)] = self.northwest
            self.cornerdict[geometry.Point(self.southwest.x_min, self.southwest.y_min)] = self.southwest
            self.cornerdict[geometry.Point(self.southeast.x_max, self.southeast.y_min)] = self.southeast

            self._directions[self.northeast] = (geometry.Direction.West, geometry.Direction.South)
            self._directions[self.northwest] = (geometry.Direction.East, geometry.Direction.South)
            self._directions[self.southwest] = (geometry.Direction.East, geometry.Direction.North)
            self._directions[self.southeast] = (geometry.Direction.West, geometry.Direction.North)

            self.complete = True

    _instance = None

    @staticmethod
    def get_instance() -> Image:
        return ImageSingleton._instance

    @staticmethod
    def has_instance() -> bool:
        return ImageSingleton._instance is not None

    @staticmethod
    def try_get_instance() -> Tuple[bool, Image]:
        return ImageSingleton.has_instance(), ImageSingleton.get_instance

    @staticmethod
    def create() -> Image:
        if(ImageSingleton._instance is not None):
            raise RuntimeError("ImageSingleton: At most one instance may exist at all times.")
        else:
            ImageSingleton._instance = ImageSingleton.Image()
            return ImageSingleton._instance

    @staticmethod
    def dispose():
        ImageSingleton._instance = None

