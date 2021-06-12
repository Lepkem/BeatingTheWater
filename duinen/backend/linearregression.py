from os import X_OK
from typing import Tuple
from . import geometry
from sklearn.linear_model import LinearRegression

def linreg(points: dict) -> Tuple[list, list]:
    """Returns arrays of respectively X and Y values"""
    X = list()
    Y = list()
    for id in sorted(points.keys()):
        X.append([points[id].y, points[id].x])
        Y.append(points[id].y)
    lr = LinearRegression()
    lr.fit(X,Y)
    return [x[1] for x in X], lr.predict(X)

def transform_coastline(x_arr: list, y_arr: list) -> Tuple[geometry.Point, geometry.Point, geometry.Slope]:
    #Extract the first boundary of the coastline and put it in a Point
    PointA = geometry.Point(x_arr[0], y_arr[0])
    #Extract the other boundary of the coastline and put it in a Point
    PointB = geometry.Point(x_arr[-1], y_arr[-1])
    #Calculate the slopes in the dimension of x and y, and put it in a Slope
    SlopeXY = geometry.Slope(PointB.y-PointA.y,PointB.x-PointA.x)

    return PointA, PointB, SlopeXY

def perpendicular_slope(coastline: geometry.Slope, dune_direction: geometry.Direction):
    if(dune_direction == geometry.Direction.East):
        #calculate the perpendicular slope in the east direction
        pass
    elif(dune_direction == geometry.Direction.West):
        #calculate the perpendicular slope in the west direction
        pass
    else:
        #TODO: Implement edge cases
        pass
    