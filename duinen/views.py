import csv, os
from django.shortcuts import render
from django.template.response import TemplateResponse
from PIL import Image
from duinen.backend.geometry import Direction
from duinen.backend.utilities import AlgorithmSettings
from django.shortcuts import render
from django.template.response import TemplateResponse
from .backend.datastruct import ImageSingleton
from .backend.algorithm import run
from duinen.backend import algorithm
from duinen.backend import topng
from .backend.topng import removeoldpng

def home(request):
    template = "home.html"
    context = {'downloadable':False}

    # Remove loaded pngs
    removeoldpng()

    # The Convert button is clicked
    if request.method == 'POST':
        lengthFromDune = int(request.POST['LFD'])
        duneHeight = int(request.POST['HEIGHT'])
        duneLength = int(request.POST['LENGTH'])
        direction = Direction.East if request.POST['OW'] == "Oost" else -1
        direction = Direction.West if request.POST['OW'] == "West" else direction
        if 'csvdoc' in request.POST is None or 'tiffdoc' in request.POST:
            context['convertOutput'] = "You need to put in a csv file and tiff image"
        else:
            context['downloadable'] = True
            # Receiving the inputs from the POST request
            csvfile = request.FILES['csvdoc'] #deprecated
            tifffile = request.FILES['tiffdoc'] #deprecated
            algosettings = AlgorithmSettings(lengthFromDune, duneHeight, duneLength, direction)

            algorithm.run(request.FILES, algosettings)

            # Turning the csv into a dict
            csvToDict = csvToDictFunction(csvfile)

            # Set pngs ready for download
            topng.convert(request)

    return render(request, template, context)


# This function takes a csv file and turns it into a dict
# MOVED TO: backend/utilities.py
def csvToDictFunction(csvinput):
    data = {}
    decoded_file = csvinput.read().decode('utf-8').splitlines()
    csvReader = csv.DictReader(decoded_file)
    for row in csvReader:
        id = row['id']
        data[id] = row
    return data
