from os import X_OK
from typing import Tuple
import datastruct
from sklearn.linear_model import LinearRegression

def linreg(points: dict) -> Tuple[list, list]:
    """Returns arrays of respectively X and Y values"""
    X = list()
    Y = list()
    for id in sorted(points.keys()):
        X.append(points[id].x)
        Y.append(points[id].y)
    lr = LinearRegression()
    lr.fit(X,Y)
    return X, lr.predict(X)

def transform_coastline(x_arr: list, y_arr: list) -> Tuple[datastruct.Point, datastruct.Point, datastruct.Slope]:
    #Extract the first boundary of the coastline and put it in a Point
    PointA = datastruct.Point(x_arr[0], y_arr[0])
    #Extract the other boundary of the coastline and put it in a Point
    PointB = datastruct.Point(x_arr[-1], y_arr[-1])
    #Calculate the slopes in the dimension of x and y, and put it in a Slope
    SlopeXY = datastruct.Slope(PointB.y-PointA.y,PointB.x-PointA.x)

    return PointA, PointB, SlopeXY

def perpendicular_slope(coastline: datastruct.Slope, dune_direction: datastruct.Direction):
    if(dune_direction == datastruct.Direction.East):
        #calculate the perpendicular slope in the east direction
        pass
    elif(dune_direction == datastruct.Direction.West):
        #calculate the perpendicular slope in the west direction
        pass
    else:
        #TODO: Implement edge cases
        pass

print(linreg())