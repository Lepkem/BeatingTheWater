from .datastruct import ImageSingleton
from .utilities import AlgorithmSettings
from .renderer import render, colortif
from .. import constants
from collections import deque
import logging
import os
from datetime import datetime
from qgis.core import *

from .topng import cout
from shutil import copyfile


qgs = QgsApplication([], False)
QgsApplication.setPrefixPath("C:\\OSGeo4W64\\apps\\qgis", True)
QgsApplication.initQgis()

def run(reqfiles: dict, settings: AlgorithmSettings):
    log_relative_path = os.path.join(os.path.dirname(__file__), 'logfile.log')
    #TODO: prevent logfile from growing endlessly as the program is executed many times
    logging.basicConfig(filename=log_relative_path, level=logging.WARNING)
    logging.info(f'Running algorithm with settings: distance={settings.distance}, threshold={settings.threshold}, minwidth={settings.min_width}, direction={settings.dune_direction}')

    #Image processing
    logging.info(f'Start of section "Image processing" at {datetime.now()}')
    if ImageSingleton.has_instance():
        ImageSingleton.dispose()
    processed_image = ImageSingleton.create()
    logging.debug(f'before populate call at {datetime.now()}')
    processed_image.populate(reqfiles, settings)
    #refit user provided parameters into the distance units of the data file
    settings.distance = settings.distance*ImageSingleton.Image.meter_to_source_unit_conversion_factor
    settings.min_width = settings.min_width*ImageSingleton.Image.meter_to_source_unit_conversion_factor
    # logging.info(f'conversion factor: {ImageSingleton.Image.meter_to_source_unit_conversion_factor}')
    # logging.info(f'dist={settings.distance}, minwidth={settings.min_width}')
    logging.debug(f'after populate call at {datetime.now()}')
    logging.info(f'End of section "Image processing" at {datetime.now()}')

    #perform algorithm stages
    logging.info(f'Start of section "Algorithm" at {datetime.now()}')

    #stage 1: Traverse the image and set up callback functions
    logging.info(f'Start of subsection "Stage 1" at {datetime.now()}')
    route_id = 0
    notify_queue = deque()
    for point in processed_image.coastline.iterable():
        node = processed_image.seek(point.x, point.y)
        dist_cum = 0.0
        while dist_cum < settings.distance:
            node, point, dist, str_dist = node.route(point, route_id, False)
            dist_cum += dist
            notify_queue.append((node, route_id))
        #logging.debug(f'Route {route_id} completed')
        route_id += 1
    logging.info(f'End of subsection "Stage 1" at {datetime.now()}')

    #stage 2: Traverse the image and trigger callback functions
    logging.info(f'Start of subsection "Stage 2" at {datetime.now()}')
    while len(notify_queue) > 0:
        node, route = notify_queue.popleft()
        logging.debug(f'calling notify with param route_id={route}')
        node.notify(route)
    logging.info(f'End of subsection "Stage 2" at {datetime.now()}')

    #stage 3: Traverse the image and determine the highest width of strong dunes per path
    if settings.marksafe:
        logging.info(f'Start of subsection "Stage 3" at {datetime.now()}')
        for point in processed_image.coastline.iterable():
            node = processed_image.seek(point.x, point.y)
            currnode = node
            dist_cum = 0.0
            str_dist_cum = 0.0
            max_dist_cum = 0.0
            while dist_cum < settings.distance:
                currnode, point, dist, str_dist = currnode.route(point, -1, max_dist_cum >= settings.min_width)
                dist_cum += dist
                str_dist_cum = (str_dist_cum + str_dist) if str_dist > 0 else 0
                if str_dist_cum > max_dist_cum:
                    max_dist_cum = str_dist_cum
                #logging.info(f'maxstr={max_dist_cum}, strcum={str_dist_cum}, strdist={str_dist}, minwidth={settings.min_width}, issafe={max_dist_cum >= settings.min_width}')
        logging.info(f'End of subsection "Stage 3" at {datetime.now()}')

    #end of algorithm
    logging.info(f'End of section "Algorithm" at {datetime.now()}')

    #render output
    logging.info(f'Start of section "Render" at {datetime.now()}')

    render(processed_image, reqfiles[constants.DATAKEY].temporary_file_path())
    colortif()
    cout()
    copyfile(os.path.join(os.path.dirname(__file__), 'output2.tif'), 'static/outputdata/converted.tif')

    logging.info(f'End of section "Render" at {datetime.now()}')

    #Cleanup
    processed_image = None
    ImageSingleton.dispose()
