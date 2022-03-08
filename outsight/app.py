import os
import logging
import argparse
import d6tflow
from pathlib import Path
from imutils import paths
from cv2 import imread
from utils.locator import PlateLocator
from utils.reader import PlateReader
from utils.searcher import PlateSearcher
from utils.display import ocrout
from utils.anonymizer import anonymize_pixelate
from utils.config import parse_configuration

if __name__ == '__main__':


    ## Set logging ##
    log_path = Path(os.path.join(Path(__file__).parents[1], 'io/app.log')).absolute()
    logging.basicConfig(filename=log_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


    ## Construct the argument parser and parse the arguments ##
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--workflow", type=str, default="all", choices=['all', 'OCR', 'Whitelist', 'Anonymize'], help="tasks to be performed")
    ap.add_argument("-minAR", "--min_aspectratio", type=int, default=2, help="# minimum aspect ratio used to detect and filter rectangular license plates")
    ap.add_argument("-maxAR", "--max_aspectratio", type=int, default=8, help="# maximum aspect ratio used to detect and filter rectangular license plates")
    ap.add_argument("-b", "--blocks", type=int, default=20, help="# of blocks for the pixelated blurring method")
    ap.add_argument("-m", "--searchmethod", type=str, default="Levenshtein", help="distance measure during the whitelist search")
    ap.add_argument("-t", "--threshold", type=int, default=1, help="distance threshold for the whitelist match")
    ap.add_argument("-c", "--clear-border", type=bool, default=False, action=argparse.BooleanOptionalAction, help="whether to clear border pixels before OCR'ing")
    ap.add_argument("-d", "--debug", type=bool, default=True, action=argparse.BooleanOptionalAction, help="whether to show additional visualizations")

    args = vars(ap.parse_args())


    ## Load the config file ##
    try:
        p = Path(os.path.join(Path(__file__).parents[1], 'CONFIG.yaml')).absolute()
        config = parse_configuration(p) 

        input = config.get("INPUT")
        input_whitelist = input + '/whitelist.txt'
        output = config.get("OUTPUT")
        output_image = output + '/imageout.png'
        output_anonym_image = output + '/anonout.png'
        output_search = output + '/searchout.txt'

    except Exception as e:
        logging.error("Problem with loading the CONFIG file", exc_info=True)

            
    ## Setup workflow ##

    # DO get training data and save it
    class GetData(d6tflow.tasks.TaskPickle):
        """
        Flow step data read from disk.
        """
        persist = ['image']

        def run(self):
            imagePath = sorted(list(paths.list_images(input)))
            image = imread(imagePath[0])  # 1st image in folder
            self.save({'image': image}) # persist/cache input data

    # DO Locate best candidate
    @d6tflow.requires(GetData)  # define dependency
    class Locate(d6tflow.tasks.TaskPickle):

        def run(self):
            image = self.inputLoad(as_dict=True)['image']  # quickly load input data
            Locator = PlateLocator(image, minAR=args["min_aspectratio"], maxAR=args["max_aspectratio"], debug=args["debug"]) 
            candidates = Locator.run_candidates(keep=5)
            (roi, lpCnt, licensePlate_col) = Locator.run_best_candidate(candidates, clearBorder=args["clear_border"])
            self.save({'roi_lpCnt': (roi, lpCnt, licensePlate_col),'image': image})   

    # DO OCR
    @d6tflow.requires(Locate)  
    class Read(d6tflow.tasks.TaskPickle):

        def run(self):
            try:
                (roi, lpCnt, licensePlate_col) = self.inputLoad(as_dict=True)['roi_lpCnt']
                if licensePlate_col.any():
                    image = self.inputLoad(as_dict=True)['image']
                    Reader = PlateReader(psm=7, oem=1, debug=args["debug"]) 
                    lpText = Reader.runOCR(roi)     
            except:
                (roi, lpCnt, licensePlate_col) = (None, None, None)
                image = None
                lpText = None
                logging.info("No license plate to be read.")
            self.save({'lpText_lpCnt': (lpText, lpCnt), 'image': image, 'roi': roi})   

    # DO Display
    @d6tflow.requires(Read)  
    class DisplayImageOCR(d6tflow.tasks.TaskPickle):

        def run(self):
            try:
                (lpText, lpCnt) = self.inputLoad(as_dict=True)['lpText_lpCnt']
            except:
                (lpText, lpCnt) = (None, None)
            if lpText:
                image = self.inputLoad(as_dict=True)['image']
                ocrout(lpText, lpCnt, image, outpath=output_image, debug=args["debug"])
            else:
                print('No license plate to display.')
                logging.info("No license plate to display.")

    # DO Anonymization
    @d6tflow.requires(Locate)  
    class Anonymize(d6tflow.tasks.TaskPickle):

        def run(self):
            try:
                (roi, lpCnt, licensePlate_col) = self.inputLoad(as_dict=True)['roi_lpCnt']
                if licensePlate_col.any():
                    image = self.inputLoad(as_dict=True)['image']
                    anonymize_pixelate(image, licensePlate_col, lpCnt, outpath=output_anonym_image, blocks=args["blocks"])
            except:
                (roi, lpCnt, licensePlate_col) = (None, None, None)
                print('No license plate to anonymize.')
                logging.info("No license plate to anonymize.")

    # DO Search plate in Whitelist
    @d6tflow.requires(Read)  
    class Search(d6tflow.tasks.TaskPickle):

        def run(self):
            try:
                (lpText, lpCnt) = self.inputLoad(as_dict=True)['lpText_lpCnt']
                if lpText:
                    Searcher = PlateSearcher(output_search, method=args["searchmethod"], threshold=args["threshold"]) 
                    Searcher.distance(lpText, input_whitelist)     
            except:
                (lpText, lpCnt) = (None, None)
                print('No license plate to search for.')
                logging.info("No license plate to search for.")


    ## Define workflow manager ##
    d6tflow.settings.log_level = 'ERROR'
    flow = d6tflow.Workflow()
    flow.preview(DisplayImageOCR)

    if args["workflow"] == 'all':
        flow.run([Search, DisplayImageOCR, Anonymize], forced_all_upstream=True, confirm=False)
    elif args["workflow"] == 'OCR':
        flow.run([DisplayImageOCR], forced_all_upstream=True, confirm=False) 
    elif args["workflow"] == 'Whitelist':
        flow.run([Search], forced_all_upstream=True, confirm=False)
    elif args["workflow"] == 'Anonymize':
        flow.run([Anonymize], forced_all_upstream=True, confirm=False)