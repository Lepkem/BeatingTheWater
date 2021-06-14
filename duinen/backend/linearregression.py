from os import X_OK
from typing import Tuple
from . import geometry
from sklearn.linear_model import LinearRegression
import math

def linreg(points: dict) -> Tuple[list, list]:
    """Returns arrays of respectively X and Y values"""
    X = list()
    Y = list()
    for id in sorted(points.keys()):
        X.append([points[id].x])
        Y.append(points[id].y)
    lr = LinearRegression()
    lr.fit(X,Y)
    Y_pred = lr.predict(X)
    return [x[0] for x in X], Y_pred

def transform_coastline(x_arr: list, y_arr: list) -> Tuple[geometry.Point, geometry.Point, geometry.Slope]:
    #Extract the first boundary of the coastline and put it in a Point
    PointA = geometry.Point(x_arr[0], y_arr[0])
    #Extract the other boundary of the coastline and put it in a Point
    PointB = geometry.Point(x_arr[-1], y_arr[-1])
    #Calculate the slopes in the dimension of x and y, and put it in a Slope
    SlopeXY = geometry.Slope((PointB.y-PointA.y)/(PointB.x-PointA.x), None)

    return PointA, PointB, SlopeXY

#source https://tutors.com/math-tutors/geometry-help/perpendicular-slope
def perpendicular_slope(coastline: geometry.Slope, dune_direction: int) -> geometry.Slope:
    """returns the perpendicular slope of the input"""
    if coastline.slope==0:
        return geometry.Slope(0, 0)
    elif dune_direction == geometry.Direction.East:
        if coastline.x_progression==0:
            return geometry.Slope(0, 1)
        else:
            return geometry.Slope(-coastline.slope**-1, 1)
    elif dune_direction == geometry.Direction.West:
        if coastline.x_progression==0:
            return geometry.Slope(0, -1)
        else:
            return geometry.Slope(-coastline.slope**-1, 1)
    else:
        raise ValueError("no matching slope and direction values")
