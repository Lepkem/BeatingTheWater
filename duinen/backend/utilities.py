import csv
from . import geometry

class AlgorithmSettings:
    def __init__(self, distance: float, threshold: float, min_width: float, dune_direction: int, marksafe: bool):
        self.distance = distance
        self.threshold = threshold
        self.min_width = min_width
        self.dune_direction = dune_direction
        self.marksafe = marksafe

def csvToDictFunction(csvinput):
    data = {}
    decoded_file = csvinput.read().decode('utf-8').splitlines()
    csvReader = csv.DictReader(decoded_file)
    for row in csvReader:
        id = row['id']
        data[id] = geometry.Point(float(row['xcoord']), float(row['ycoord']))
    return data