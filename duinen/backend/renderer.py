from typing import Tuple
import gdal
import os
from datastruct import ImageSingleton
import django

def render(image: ImageSingleton.Image, source_filepath: str):
    target_path = os.path.join(os.path.dirname(__file__), '..\output.tif')
    #TODO: Check if gtif driver exists
    driver_tiff = gdal.GetDriverByName("GTiff")
    #TODO: Why float32?
    renderlayer = driver_tiff.Create(target_path, image.x_max, image.y_max, bands=1, eType=gdal.GDT_Float32)
    with gdal.Open(source_filepath) as sf:
        renderlayer.SetGeoTransform(sf.GetGeoTransform())
        renderlayer.SetProjection(sf.GetProjection())
    pixelband = renderlayer.GetRasterBand(1).ReadAsArray()
    with QgsRasterLayer(source_filepath, "sourcefile") as rlayer:
        xmin = rlayer.extent().xMinimum()
        ymin = rlayer.extent().yMinimum()
    xoffs, yoffs = find_offset_xy(xmin, ymin, image.x_min, image.y_min, ImageSingleton.Image.resolution)
    xmaxoffs, ymaxoffs = find_offset_xy(xmin, ymin, image.x_max, image.y_max)
    xpointer = image.x_min
    ypointer = image.y_min
    for column in range(xoffs, xmaxoffs):
        for row in range(yoffs, ymaxoffs):
            pixelband[row][column] = image.seek(xpointer, ypointer)._rating
            ypointer += ImageSingleton.Image.resolution
        xpointer += ImageSingleton.Image.resolution
        ypointer = image.y_min
    renderlayer.GetRasterBand(1).WriteArray(pixelband)
    #TODO: render colors
    #TODO: save output file and return it

def find_offset_xy(xmin: float, ymin: float, xtarget:float, ytarget: float, resolution: float) -> Tuple[float, float]:
    find_offset = lambda min, target: int(((target - min) - (target%resolution))//resolution)
    return find_offset(xmin, xtarget), find_offset(ymin, ytarget)
