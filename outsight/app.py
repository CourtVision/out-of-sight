import os
import d6tflow
import logging
import argparse
from pathlib import Path
from imutils import paths
from cv2 import imread
from utils.locator import PlateLocator
from utils.reader import PlateReader
from utils.searcher import PlateSearcher
from utils.display import ocrout
from utils.config import parse_configuration
# TODO itils.anonymizer


# Set logging #
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_path = Path(os.path.join(Path(__file__).parents[1], 'app.log')).absolute()
logging.basicConfig(filename=log_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s')


# Construct the argument parser and parse the arguments #
ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--input", required=True,	help="path to input directory of images")
# ap.add_argument("-o", "--output", required=True, help="path to output directory of images")
ap.add_argument("-w", "--workflow", default="all", help="tasks to be performed")
ap.add_argument("-c", "--clear-border", type=int, default=-1, help="whether or to clear border pixels before OCR'ing")
ap.add_argument("-p", "--psm", type=int, default=7,	help="default PSM mode for OCR'ing license plates")
ap.add_argument("-om", "--oem", type=int, default=3, help="default engine mode for OCR'ing license plates")
ap.add_argument("-d", "--debug", type=int, default=False, help="whether or not to show additional visualizations")
ap.add_argument("-m", "--searchmethod", default="Levenshtein", help="distance measure of list whitelist search")
ap.add_argument("-t", "--threshold", type=int, default=1, help="distance threshold for the whitelist match")

args = vars(ap.parse_args())

# Load the config file
try:
    p = Path(os.path.join(Path(__file__).parents[1], 'CONFIG.yaml')).absolute()  # one level up
    config = parse_configuration(p) 

    input = config.get("INPUT")
    output = config.get("OUTPUT")
    input_whitelist = input + '/whitelist.txt'
    output_image = output + '/imageout.jpg'
    output_search = output + '/searchout.txt'
# TODO output_image = config.get("OUTPUT") + '/out.jpg'

except Exception as e:
    logging.error("Problem with loading the CONFIG file", exc_info=True)

        
# Setup workflow #

# DO get training data and save it
logging.info("Start getting the image...")
class GetData(d6tflow.tasks.TaskPickle):

    persist = ['image']
    def run(self):
        imagePath = sorted(list(paths.list_images(input)))
        image = imread(imagePath[0])  # 1st image in folder
        self.save({'image': image}) # persist/cache input data

# DO Locate best candidate
logging.info("Start searching for license plate...")
@d6tflow.requires(GetData)  # define dependency
class Locate(d6tflow.tasks.TaskPickle):

    def run(self):
        image = self.inputLoad(as_dict=True)['image']  # quickly load input data
        # apply automatic license plate recognition
        Locator = PlateLocator(minAR=4, maxAR=5, debug=args["debug"]) 
        candidates, gray = Locator.run_candidates(image, keep=5)
        (roi, lpCnt) = Locator.run_best_candidate(gray, candidates, clearBorder=args["clear_border"] > 0)
        self.save({'roi_lpCnt': (roi, lpCnt),'image': image})   

# DO OCR
logging.info("Start OCRing...")
@d6tflow.requires(Locate)  
class Read(d6tflow.tasks.TaskPickle):

    def run(self):
        (roi, lpCnt) = self.inputLoad(as_dict=True)['roi_lpCnt']
        image = self.inputLoad(as_dict=True)['image']
        # apply automatic license plate recognition
        Reader = PlateReader(minAR=4, maxAR=5, psm=args["psm"], oem=args["oem"], debug=args["debug"]) 
        lpText = Reader.runOCR(roi)     
        self.save({'lpText_lpCnt': (lpText, lpCnt), 'image': image})   

# DO Display
logging.info("Save recognized image...")
@d6tflow.requires(Read)  
class DisplayImageOCR(d6tflow.tasks.TaskPickle):

    def run(self):
        (lpText, lpCnt) = self.inputLoad(as_dict=True)['lpText_lpCnt']
        image = self.inputLoad(as_dict=True)['image']
        ocrout(lpText, lpCnt, image, outpath=output_image, debug=args["debug"])
        self.save({'lpCnt': lpCnt})   

# DO Search plate in Whitelist
logging.info("Looking for current license plate in the list of whitelisted ones...")
@d6tflow.requires(Read)  
class Search(d6tflow.tasks.TaskPickle):

    def run(self):
        (lpText, lpCnt) = self.inputLoad(as_dict=True)['lpText_lpCnt']
        Searcher = PlateSearcher(output_search, method=args["searchmethod"], threshold=args["threshold"]) 
        Searcher.distance(lpText, input_whitelist)     

# DO Anonymize
# TODO 
#@d6tflow.requires(OCR)  
#class SaveAnonymImage(d6tflow.tasks.TaskPickle):
#
#    def run(self):
#        (lpText, lpCnt, image) = self.inputLoad()  # quickly load input data
#        # TODO 



if __name__ == '__main__':

    # Define workflow manager
    flow = d6tflow.Workflow()
    flow.preview(DisplayImageOCR)

    if args["workflow"] == 'all':
        flow.run([Search,DisplayImageOCR], forced_all_upstream=True, confirm=False)  # multiple tasks,SearchDB,SaveAnonymImage

    elif args["workflow"] == 'OCR':
        flow.run([DisplayImageOCR], forced_all_upstream=True, confirm=False)  

    #elif args["workflow"] == 'SaveAnonymImage':
    #    flow.run([SaveAnonymImage])

    


# PDOC
# pdoc -o ./docs ./shelter.py
# """
#   Given a URL, return the `requests` response object.#
#
#   Args:
#       url (str): URL to scrape.#
#
#   Returns:
#        requests.models.Response: `requests` response object.
#"""