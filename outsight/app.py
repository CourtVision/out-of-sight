if __name__ == '__main__':


    import os
    import d6tflow
    import logging
    import argparse
    from imutils import paths
    from cv2 import imread
    from utils.locator import PlateLocator
    from utils.reader import OCR
    from utils.display import ocrout
    from utils.config import parse_configuration
    # TODO itils.anonymizer
    # TODO utils.dbsearch


    # Set logging #
    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    #try:
    #      c = a / b
    #except Exception as e:
    #    logging.error("Exception occurred", exc_info=True)


    # Construct the argument parser and parse the arguments #
    ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--input", required=True,	help="path to input directory of images")
    # ap.add_argument("-o", "--output", required=True, help="path to output directory of images")
    ap.add_argument("-w", "--workflow", required=True, default="all", help="tasks to be performed")
    ap.add_argument("-c", "--clear-border", type=int, default=-1, help="whether or to clear border pixels before OCR'ing")
    ap.add_argument("-p", "--psm", type=int, default=7,	help="default PSM mode for OCR'ing license plates")
    ap.add_argument("-om", "--oem", type=int, default=2, help="default engine mode for OCR'ing license plates")
    ap.add_argument("-d", "--debug", type=int, default=False, help="whether or not to show additional visualizations")
    args = vars(ap.parse_args())

    config = parse_configuration(os.path.dirname(os.path.realpath(__file__))+"/CONIFG.yaml")
    input = config.get("INPUT")

    # Setup workflow #

    # DO get training data and save it
    class GetData(d6tflow.tasks.TaskPickle):
        persist = ['image']
        def run(self):
            imagePath = sorted(list(paths.list_images(input)))
            image = imread(imagePath[0])  # 1st image in folder
            self.save({'image': image}) # persist/cache input data

    # DO Locate best candidate
    @d6tflow.requires(GetData)  # define dependency
    class Locate(d6tflow.tasks.TaskPickle):

        def run(self):
            image = self.inputLoad()  # quickly load input data
            # apply automatic license plate recognition
            Locator = PlateLocator(minAR=4, maxAR=5, debug=args["debug"]) 
            candidates, gray = Locator.run_candidates(image, keep=5)
            (roi, lpCnt) = Locator.run_best_candidate(gray, candidates, clearBorder=args["clear_border"] > 0)
            self.save({'roi': roi, 'lpCnt': lpCnt,'image': image})  # persist/cache 

    # DO OCR
    @d6tflow.requires(Locate)  # define dependency
    class OCR(d6tflow.tasks.TaskPickle):

        def run(self):
            (roi, lpCnt, image) = self.inputLoad()  # quickly load input data
            # apply automatic license plate recognition
            OCRing = OCR(minAR=4, maxAR=5, debug=args["debug"]) 
            (lpText, lpCnt) = OCRing.run(roi, lpCnt, psm=args["psm"], oem=args["oem"])        
            self.save((lpText, lpCnt, image))  # persist/cache 

    # DO Display
    @d6tflow.requires(OCR)  # define dependency
    class DisplayImageOCR(d6tflow.tasks.TaskPickle):

        def run(self):
            (lpText, lpCnt, image) = self.inputLoad()  # quickly load input data
            ocrout(lpText, lpCnt, image, debug=args["debug"])

    # DO Anonymize
    # TODO 
    #@d6tflow.requires(OCR)  # define dependency
    #class SaveAnonymImage(d6tflow.tasks.TaskPickle):
    #
    #    def run(self):
    #        (lpText, lpCnt, image) = self.inputLoad()  # quickly load input data
    #        # TODO 

    # DO Serch plate in DB
    # TODO 
    #@d6tflow.requires(OCR)  # define dependency
    #class SearchDB(d6tflow.tasks.TaskPickle):
    #
    #    def run(self):
    #        (lpText, lpCnt, image) = self.inputLoad()  # quickly load input data
    #        # TODO 


    # Define workflow manager
    flow = d6tflow.WorkflowMulti()
    flow.reset_upstream(confirm=False) # DEMO ONLY: force re-run
    
    if args["workflow"] == 'all':
        flow.run([DisplayImageOCR])  # multiple tasks  ,SearchDB,SaveAnonymImage
    
    elif args["workflow"] == 'OCR':
        flow.run([DisplayImageOCR])  

#    elif args["workflow"] == 'SearchDB':
#        flow.run([SearchDB])  

#    elif args["workflow"] == 'SaveAnonymImage':
#        flow.run([SaveAnonymImage])



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