import csv, os
from django.shortcuts import render
from django.template.response import TemplateResponse
from PIL import Image
from django.shortcuts import render
from django.template.response import TemplateResponse

def convert(request):
    removeoldpng()

    # The Convert button is clicked
    if request.method == 'POST':
        if 'csvdoc' in request.POST is None or 'tiffdoc' in request.POST:
            context['convertOutput'] = "You need to put in a csv file and tiff image"
        else:
            # Receiving the inputs from the POST request
            tifffile = request.FILES['tiffdoc'] #deprecated

            # Passing the data to template (The data below here should later be replaced by the algoritm's output: a tiff image and download button)
            tiffImage = Image.open(tifffile)
            tiffImage = tiffImage.convert('RGB')
            tiffImage.save("static/outputdata/tiffToPng.png", "PNG")
            # raise Exception("Sorry, no numbers below zero")

def removeoldpng():
    if os.path.exists("static/outputdata/tiffToPng.png"):
        os.remove("static/outputdata/tiffToPng.png")

def removefiles():
    if os.path.exists("static/outputdata/converted.tif"):
        os.remove("static/outputdata/converted.tif")
    if os.path.exists("static/outputdata/converted.png"):
        os.remove("static/outputdata/converted.png")

def cout():

    # Passing the data to template (The data below here should later be replaced by the algoritm's output: a tiff image and download button)
    tiffImage = Image.open(os.path.join(os.path.dirname(__file__), 'output2.tif'))
    tiffImage = tiffImage.convert('RGB')
    tiffImage.save("static/outputdata/converted.png", "PNG")
    # raise Exception("Sorry, no numbers below zero")
