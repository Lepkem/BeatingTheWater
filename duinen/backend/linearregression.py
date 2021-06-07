from typing import Tuple
from .datastruct import Point, Slope as Point, Slope
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
    #Extract the other boundary of the coastline and put it in a Point
    #Calculate the slopes in the dimension of x and y, and put it in a Slope
    raise NotImplementedError()

print(linreg())