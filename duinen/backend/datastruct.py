from __future__ import annotations
import enum
import logging
from math import sqrt
import math
import numpy as np
from typing import Tuple
import os, tempfile
from .. import constants
from qgis.core import *
from . import geometry, utilities, linearregression

class Rating(enum.Enum):
    Weak = 1
    StrongNoOverlap = 2
    Strong = 3

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
        self.visited = False

        self._rating = Rating.Strong if (height >= self.threshold) else Rating.Weak
        self.subscribers = list()
        self._notify = None

    def _downgrade_rating(self):
        logging.debug(f'downgrade_rating func at {self}, rating before: {self._rating} strong: {self._rating == Rating.Strong}')
        if self._rating == Rating.Strong:
            self._rating = Rating.StrongNoOverlap

    def _notify_factory(self, this_route_id : int) -> function:
        def notify(route_id : int, rating : int):
            logging.debug(f'generated notify function at {self} with params: thisroute={this_route_id}, route={route_id}, rating={rating}')
            if this_route_id != route_id and rating == Rating.Weak:
                self._downgrade_rating()
        return notify
    
    def notify(self, route_id : int):
        logging.debug(f'notify function at {self} with rating: {self._rating} for subscribers: {self.subscribers}')
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
        if direction == geometry.Direction.East:
            return self._east
        elif direction == geometry.Direction.North:
            return self._north
        elif direction == geometry.Direction.West:
            return self._west
        elif direction == geometry.Direction.South:
            return self._south
        else:
            raise ValueError("Invalid direction")

    def _is_within(self, point : geometry.Point) -> bool:
        if(point.x < self.x_min or point.x > self.x_max):
            return False
        if(point.y < self.y_min or point.y > self.y_max):
            return False
        return True

    def _calculate_out(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        if(self.slope.slope == 0 or self.slope.x_progression == 0):
            return self._intersect_axis(entry)
        elif(self.slope.slope > 0 and self.slope.x_progression > 0):
            return self._intersect_first(entry)
        elif(self.slope.slope < 0 and self.slope.x_progression < 0):
            return self._intersect_second(entry)
        elif(self.slope.slope > 0 and self.slope.x_progression < 0):
            return self._intersect_third(entry)
        elif(self.slope.slope < 0 and self.slope.x_progression > 0):
            return self._intersect_fourth(entry)
        else:
            raise ValueError("Invalid slope.")


    def _intersect_axis(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        if(self.slope.slope == 0 and self.slope.x_progression > 0):
            return geometry.Point(self.x_max, entry.y), self._east
        elif(self.slope.x_progression == 0 and self.slope.slope > 0):
            return geometry.Point(entry.x, self.y_max), self._north
        elif(self.slope.slope == 0 and self.slope.x_progression < 0):
            return geometry.Point(self.x_min, entry.y), self._west
        elif(self.slope.x_progression == 0 and self.slope.slope < 0):
            return geometry.Point(entry.x, self.y_min), self._south
        else:
            raise AttributeError()

    def _intersect_first(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_max - entry.x
        dy = self.y_max - entry.y
        dx_derived = dy/self.slope.slope
        if(dx < dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.slope), self._east
        elif(dx > dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._north
        else:
            next = self._north._east if self._north is not None and self._north._east is not None else None
            next = self._east._north if self._east is not None and self._east._north is not None else next
            return geometry.Point(self.x_max, self.y_max), next

    def _intersect_second(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_min - entry.x
        dy = self.y_max - entry.y
        dx_derived = dy/self.slope.slope
        if(dx > dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.slope), self._west
        elif(dx < dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._north
        else:
            next = self._north._west if self._north is not None and self._north._west is not None else None
            next = self._west._north if self._west is not None and self._west._north is not None else next
            return geometry.Point(self.x_min, self.y_max), next


    def _intersect_third(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_min - entry.x
        dy = self.y_min - entry.y
        dx_derived = dy/self.slope.slope
        if(dx > dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.slope), self._west
        elif(dx < dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._south
        else:
            next = self._south._west if self._south is not None and self._south._west is not None else None
            next = self._west._south if self._west is not None and self._west._south is not None else next
            return geometry.Point(self.x_min, self.y_min), next


    def _intersect_fourth(self, entry : geometry.Point) -> Tuple[geometry.Point, Node]:
        dx = self.x_max - entry.x
        dy = self.y_min - entry.y
        dx_derived = dy/self.slope.slope
        if(dx < dx_derived):
            return geometry.Point(entry.x + dx, entry.y + dx*self.slope.slope), self._east
        elif(dx > dx_derived):
            return geometry.Point(entry.x + dx_derived, entry.y + dy), self._south
        else:
            next = self._south._east if self._south is not None and self._south._east is not None else None
            next = self._east._south if self._east is not None and self._east._south is not None else next
            return geometry.Point(self.x_max, self.y_min), next

    def _subscribe_neighbors(self):
        if(self._notify is None):
            raise AttributeError("Notify callback function is not defined.")
        
        northeast = False
        northwest = False
        southwest = False
        southeast = False
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
    def route(self, entry : geometry.Point, route_id : int) -> Tuple[Node, geometry.Point, float, float]:
        #TODO: Fix floating point inaccuracy
        # if(not self._is_within(entry)):
        #     xrange = (self.x_min, self.x_max)
        #     yrange = (self.y_min, self.y_max)
        #     entryxy = (entry.x, entry.y)
        #     slope = Node.slope.slope
        #     raise ValueError("Entry point out of boundary.")
        if route_id != -1:
            self.visited = True
            self._notify = self._notify_factory(route_id)
            if(self._rating == Rating.Strong):
                self._subscribe_neighbors()
        out, next = self._calculate_out(entry)
        distance = entry.distance(out)
        strongdistance = distance if self._rating == Rating.Strong else 0
        return next, out, distance, strongdistance

class ImageSingleton:
    class Image:
        class Coastline:
            def __init__(self, start: geometry.Point, stop: geometry.Point, slope: geometry.Slope):
                self.start = start
                self.stop = stop
                self.slope = slope

            def iterable(self) -> list:
                xdiff = self.stop.x - self.start.x
                dx = None
                dy = None
                if xdiff > 0:
                    if self.slope.slope > 1 or self.slope.slope < -1:
                        #dy is the determining factor
                        dy = ImageSingleton.Image.resolution if self.slope.slope > 0 else -ImageSingleton.Image.resolution
                        dx = dy/self.slope.slope
                        pass
                    else:
                        #dx is the determining factor
                        dx = ImageSingleton.Image.resolution
                        dy = dx*self.slope.slope
                        pass
                elif xdiff < 0:
                    if self.slope.slope > 1 or self.slope.slope < -1:
                        #dy is the determining factor
                        dy = ImageSingleton.Image.resolution if self.slope.slope > 0 else -ImageSingleton.Image.resolution
                        dx = -(dy/self.slope.slope)
                        pass
                    else:
                        #dx is the determining factor
                        dx = -ImageSingleton.Image.resolution
                        dy = dx*self.slope.slope
                        pass
                else:
                    dx = 0
                    dy = ImageSingleton.Image.resolution if self.slope.slope > 0 else -ImageSingleton.Image.resolution
                curr = self.start
                iter = list()
                while(curr.x <= self.stop.x): #checking y is redundant
                    iter.append(curr)
                    curr = geometry.Point(curr.x + dx, curr.y + dy)
                return iter

            def distance_between(self):
                a = ImageSingleton.Image.resolution
                b = ImageSingleton.Image.resolution*self.slope.slope
                return sqrt(a**2 + b**2)

        resolution = None   #Type: Float
        coastline = None    #Type: Coastline
        meter_to_source_unit_conversion_factor = None

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
            start, stop, slope = linearregression.transform_coastline(xvals, yvals)
            ImageSingleton.Image.coastline = ImageSingleton.Image.Coastline(start, stop, slope)
            Node.slope = linearregression.perpendicular_slope(self.coastline.slope, settings.dune_direction)
            Node.threshold = settings.threshold
            #complete the code above
            #process image pixels into nodes
            #TODO: replace hardcoded file path
            #data_file = "C:\\Users\\Alexander\\Desktop\\ProjectD_Data\\SpringertduinenAHNhoogdynamisch\\H_2m_2019_Springertduinen.tif"
            #TODO: throws a bunch of non-fatal errors
            temppath = inputfiles[constants.DATAKEY].temporary_file_path()
            rlayer = QgsRasterLayer(temppath, "datafile")
            crs = rlayer.crs()
            source_unit = crs.mapUnits()
            ImageSingleton.Image.meter_to_source_unit_conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceMeters, source_unit)
            if rlayer.rasterUnitsPerPixelY() == rlayer.rasterUnitsPerPixelX():
                ImageSingleton.Image.resolution = rlayer.rasterUnitsPerPixelX()
            else:
                raise ValueError("The program only supports square pixels.")
            find_boundary = lambda refval, outerval, step, sign: refval - ((refval - outerval) % step)*sign
            corners = self._get_essential_area_corners(settings.distance)
            self.x_min = find_boundary(min([point.x for point in corners]), rlayer.extent().xMinimum(), rlayer.rasterUnitsPerPixelX(), 1)
            self.x_max = find_boundary(max([point.x for point in corners]), rlayer.extent().xMaximum(), rlayer.rasterUnitsPerPixelX(), -1)
            self.y_min = find_boundary(min([point.y for point in corners]), rlayer.extent().yMinimum(), rlayer.rasterUnitsPerPixelY(), 1)
            self.y_max = find_boundary(max([point.y for point in corners]), rlayer.extent().yMaximum(), rlayer.rasterUnitsPerPixelY(), -1)

            #TODO: Link neighbor nodes
            outer = 0
            for x in np.arange(self.x_min, self.x_max, rlayer.rasterUnitsPerPixelX()):
                inner = 0
                for y in np.arange(self.y_min, self.y_max, rlayer.rasterUnitsPerPixelY()):
                    sample, success = rlayer.dataProvider().sample(QgsPointXY(x + rlayer.rasterUnitsPerPixelX()/2, y + rlayer.rasterUnitsPerPixelY()/2), 1)
                    newNode = Node(x, x + rlayer.rasterUnitsPerPixelX(), y, y + rlayer.rasterUnitsPerPixelY(), sample if success else 0)
                    if outer == 0:
                        self.northwest = newNode
                        if inner == 0:
                            self.southwest = newNode
                    if inner == 0:
                        if self.southeast is not None:
                            newNode.link_neighbor(self.southeast, geometry.Direction.West)
                        self.southeast = newNode
                    elif self.northeast is not None:
                        newNode.link_neighbor(self.northeast, geometry.Direction.South)
                        if outer != 0:
                            newNode.link_neighbor(self.northeast.get_neighbor(geometry.Direction.West).get_neighbor(geometry.Direction.North), geometry.Direction.West)
                    self.northeast = newNode
                    inner = 1
                outer = 1
            #set up navigation dictionaries
            self._finish()

        def seek(self, x: float, y: float) -> Node:
            self._checkComplete()

            def closest(min: float, max: float, value: float) -> Tuple[float, float]:
                mindist = abs(value - min)
                maxdist = abs(max - value)
                return (min, mindist) if mindist <= maxdist else (max, maxdist)
            startx, distx = closest(self.x_min, self.x_max, x)
            starty, disty = closest(self.y_min, self.y_max, y)
            ###DEBUG###
            #xvals = [p.x for p in self.cornerdict.keys()]
            #yvals = [p.y for p in self.cornerdict.keys()]
            ###\DEBUG###
            curr = self.cornerdict(startx, starty)
            dirx, diry = self._directions.get(curr)
            while distx >= self.resolution:
                curr = curr.get_neighbor(dirx)
                distx -= self.resolution
            while disty >= self.resolution:
                curr = curr.get_neighbor(diry)
                disty -= self.resolution

            return curr

        def _get_essential_area_corners(self, distance: float) -> list[geometry.Point]:
            points = list()
            for pointA in [self.coastline.start, self.coastline.stop]:
                points.append(pointA)
                alfa = math.atan(abs(Node.slope.slope))
                dx = math.cos(alfa)*distance*Node.slope.dx_sign()
                dy = math.sin(alfa)*distance*Node.slope.dy_sign()
                points.append(geometry.Point(pointA.x + dx, pointA.y + dy))
            return points
            
        def _checkComplete(self):
            if not self.complete:
                raise AttributeError("Can't read image while processing is not complete.")
        
        def _finish(self):
            def make_dict_emulator():
                def dict_emulator(x, y):
                    if(x == self.x_min):
                        if y == self.y_max:
                            return self.northwest
                        elif y == self.y_min:
                            return self.southwest
                        else:
                            raise RuntimeError("Y dimension mismatch")
                    elif(x == self.x_max):
                        if y == self.y_max:
                            return self.northeast
                        elif y == self.y_min:
                            return self.southeast
                        else:
                            raise RuntimeError("Y dimension mismatch")
                    else:
                        raise RuntimeError("X dimension mismatch")
                return dict_emulator


            self.cornerdict = make_dict_emulator()
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

