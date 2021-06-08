import csv
from duinen.backend.datastruct import Point

def csvToDictFunction(csvinput):
    data = {}
    decoded_file = csvinput.read().decode('utf-8').splitlines()
    csvReader = csv.DictReader(decoded_file)
    for row in csvReader:
        id = row['id']
        data[id] = Point(float(row['xcoord']), float(row['ycoord']))
    return data