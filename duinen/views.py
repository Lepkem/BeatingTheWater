import csv
from django.shortcuts import render
from django.template.response import TemplateResponse
from .backend.datastruct import ImageSingleton

def home(request):
    template = "home.html"
    context = {}

    # The Convert button is clicked
    if request.method == 'POST':
        if 'csvdoc' in request.POST is None or 'tiffdoc' in request.POST:
            context['convertOutput'] = "You need to put in a csv file and tiff image"
        else:
            # Receiving the inputs from the POST request
            csvfile = request.FILES['csvdoc'] #deprecated
            tifffile = request.FILES['tiffdoc'] #deprecated

            processed_image = ImageSingleton.create()
            processed_image.populate(request.FILES)

            # Turning the csv into a dict 
            csvToDict = csvToDictFunction(csvfile)
            
            # Passing the data to template (The data below here should later be replaced by the algoritm's output: a tiff image and download button)
            context['convertOutput'] = csvToDict.__str__() + tifffile.name
            

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
                    
