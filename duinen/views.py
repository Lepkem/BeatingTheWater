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
from .backend.topng import removefiles

def home(request):
    template = "home.html"
    context = {'downloadable':False}

    # Remove loaded pngs
    removeoldpng()
    removefiles()

    # The Convert button is clicked
    if request.method == 'POST':
        if 'csvdoc' in request.POST is None or 'tiffdoc' in request.POST:
            context['convertOutput'] = "You need to put in a csv file and tiff image"
        else:
            lengthFromDune = int(request.POST['LFD'])
            duneHeight = int(request.POST['HEIGHT'])
            duneLength = int(request.POST['LENGTH'])
            duneStrong = bool(request.POST['SUPERSTRONG'])
            direction = Direction.East if request.POST['OW'] == "Oost" else -1
            direction = Direction.West if request.POST['OW'] == "West" else direction
            #TODO: replace True with user input value from checkbox
            algosettings = AlgorithmSettings(lengthFromDune, duneHeight, duneLength, direction, True)

            algorithm.run(request.FILES, algosettings)
            context['downloadable'] = True

            # Passing the data to template (The data below here should later be replaced by the algoritm's output: a tiff image and download button)
            topng.convert(request)
            context['convertOutput'] = "Algorithm run was succesful"


    return render(request, template, context)
