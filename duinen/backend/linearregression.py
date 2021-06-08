from os import X_OK
from typing import Tuple
from .datastruct import Point, Slope as Point, Slope, Direction
import pandas as pd
from sklearn.linear_model import LinearRegression

def linreg() -> Tuple[list, list]:
    """Returns arrays of respectively X and Y values"""
    data = pd.read_csv('Coord.csv')
    X = data.iloc[:,1].values.reshape(-1,1)
    Y = data.iloc[:,2].values.reshape(-1,1)
    lr = LinearRegression()
    lr.fit(X,Y)
    return X, lr.predict(X)

def transform_coastline(x_arr: list, y_arr: list) -> Tuple[Point, Point, Slope]:
    #Extract the first boundary of the coastline and put it in a Point
    PointA = Point(x_arr[0], y_arr[0])
    #Extract the other boundary of the coastline and put it in a Point
    PointB = Point(x_arr[-1], y_arr[-1])
    #Calculate the slopes in the dimension of x and y, and put it in a Slope
    SlopeXY = Slope(PointB.y-PointA.y,PointB.x-PointA.x)

    return PointA, PointB, SlopeXY

def perpendicular_slope(coastline: Slope, dune_direction: Direction):
    if(dune_direction == Direction.East):
        #calculate the perpendicular slope in the east direction
        pass
    elif(dune_direction == Direction.West):
        #calculate the perpendicular slope in the west direction
        pass
    else:
        #TODO: Implement edge cases
        pass

print(linreg())