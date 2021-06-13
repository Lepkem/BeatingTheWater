from .datastruct import ImageSingleton
from .utilities import AlgorithmSettings
from collections import deque

def run(reqfiles: dict, settings: AlgorithmSettings):
    #Image processing
    if ImageSingleton.has_instance():
        ImageSingleton.dispose()
    processed_image = ImageSingleton.create()
    processed_image.populate(reqfiles, settings)

    #perform algorithm stages

    #stage 1: Traverse the image and set up callback functions
    route_id = 0
    notify_queue = deque()
    for point in processed_image.coastline.iterable():
        node = processed_image.seek(point.x, point.y)
        dist_cum = 0.0
        while dist_cum < settings.distance:
            node, point, dist, str_dist = node.route(point, route_id)
            dist_cum += dist
            notify_queue.append((node, route_id))
        route_id += 1
            
    #stage 2: Traverse the image and trigger callback functions
    while len(notify_queue) > 0:
        node, route = notify_queue.popleft()
        node.notify(route)

    #stage 3: Traverse the image and determine the highest width of strong dunes per path
    strongwidths = dict()
    for point in processed_image.coastline.iterable():
        node = processed_image.seek(point.x, point.y)
        currnode = node
        dist_cum = 0.0
        str_dist_cum = 0.0
        while dist_cum < settings.distance:
            currnode, point, dist, str_dist = currnode.route(point, -1)
            dist_cum += dist
            str_dist_cum += str_dist
        strongwidths[node] = str_dist_cum

    #end of algorithm

    #render output

    #Cleanup
    processed_image = None
    ImageSingleton.dispose()