from typing import Tuple
import gdal
import os
from .datastruct import ImageSingleton
from qgis.core import *
import sys
sys.path.append('C:\\OSGeo4W64\\apps\\qgis\\python\\plugins')
import processing

def render(image: ImageSingleton.Image, source_filepath: str):
    target_path = os.path.join(os.path.dirname(__file__), 'output.tif')
    #TODO: Check if gtif driver exists
    driver_tiff = gdal.GetDriverByName("GTiff")
    rlayer = QgsRasterLayer(source_filepath, "sourcefile")
    xmin = rlayer.extent().xMinimum()
    ymin = rlayer.extent().yMinimum()
    xoffs, yoffs = find_offset_xy(xmin, ymin, image.x_min, image.y_min, ImageSingleton.Image.resolution)
    xmaxoffs, ymaxoffs = find_offset_xy(xmin, ymin, image.x_max, image.y_max, ImageSingleton.Image.resolution)
    #TODO: Why float32?
    renderlayer = driver_tiff.Create(target_path, xsize=xmaxoffs, ysize=ymaxoffs, bands=1, eType=gdal.GDT_Float32)
    sf = gdal.Open(source_filepath)
    renderlayer.SetGeoTransform(sf.GetGeoTransform())
    renderlayer.SetProjection(sf.GetProjection())
    pixelband = renderlayer.GetRasterBand(1).ReadAsArray()
    
    xpointer = image.x_min
    ypointer = image.y_min
    for column in range(xoffs, xmaxoffs):
        for row in range(yoffs, ymaxoffs):
            #rating = image.seek(xpointer, ypointer)._rating.value
            pixelband[row][column] = image.seek(xpointer, ypointer)._rating.value
            ypointer += ImageSingleton.Image.resolution
        xpointer += ImageSingleton.Image.resolution
        ypointer = image.y_min
    renderlayer.GetRasterBand(1).WriteArray(pixelband)
    #TODO: render colors
    color_conf = os.path.join(os.path.dirname(__file__), 'color_conf.txt')

    from processing.core.Processing import Processing
    Processing.initialize()
    # prints = list()
    # for alg in QgsApplication.processingRegistry().algorithms():
    #     prints.append(alg.id() + "->" + alg.displayName())
    processing.run("gdal:colorrelief", {'INPUT': source_filepath,
        'BAND': 1,
        'COMPUTE_EDGES': False,
        'COLOR_TABLE': color_conf,
        'MATCH_MODE:': 0,
        'OPTIONS' : "",
        'OUTPUT' : target_path
    })
    #TODO: save output file and return it

def find_offset_xy(xmin: float, ymin: float, xtarget:float, ytarget: float, resolution: float) -> Tuple[float, float]:
    find_offset = lambda min, target: int(((target - min) - (target%resolution))//resolution)
    return find_offset(xmin, xtarget), find_offset(ymin, ytarget)
