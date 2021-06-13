from .datastruct import ImageSingleton
from .utilities import AlgorithmSettings

def run(reqfiles: dict, settings: AlgorithmSettings):
    #Image processing
    if ImageSingleton.has_instance():
        ImageSingleton.dispose()
    processed_image = ImageSingleton.create()
    processed_image.populate(reqfiles, settings)

    #perform algorithm stages

    #stage 1: Traverse the image and set up callback functions
    
    #stage 2: Traverse the image and trigger callback functions

    #stage 3: Traverse the image and determine the highest width of strong dunes per path

    #end of algorithm

    #render output

    #Cleanup
    processed_image = None
    ImageSingleton.dispose()