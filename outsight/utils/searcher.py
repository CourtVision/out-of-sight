import pandas as pd
from Levenshtein import distance
import logging
logger = logging.getLogger(__name__)

class PlateSearcher():
    """
    Class to compare a string with a whitlist of strings.
    
    Args:
    ------------
        method (str): Comparision method, Default=Levenshtein
        threshold (int): Level of deviation (due to OCRing problems) to accept license plate
        output_search (str): Path of list of results persisted in a text file
    """
    def __init__(self, output_search: str, method: str = 'Levenshtein', threshold: int = 1):

        self.method = method       # more methods to be added if needed
        self.threshold = threshold
        self.output_search = output_search

    def load_list(self, path: str):
        """
        Load a list from disk.        
        Args:
        ------------
            path (str): Path of list of whitelisted license plates text file

        Returns:
        ------------
            whitelist (list): Python list generated from a text file     
        """
        try:
            with open(path, 'r') as f:
                whitelist = [plate.rstrip() for plate in f]
            return whitelist
        except Exception as e:
            logger.error("Problem with loading the whitlelist file", exc_info=True)

    def distance(self, plate: str, listpath: str):
        """
        Checks the similarity between each element of a list and a text.
        
        Args:
        ------------
            plate (str): String of license plate in question
            listpath (str): Path of list of whitelisted license plates text file

        Returns:
        ------------
            None. Prints and saves results in text file.         
        """
        whitelist = self.load_list(listpath)
        distances = []
        for i in whitelist:
            if self.method=='Levenshtein':    
                d = distance(plate.rstrip().replace(' ', ''), i)  # remove trailing newline
            distances.append(d)
            dist_dict = dict(zip(whitelist, distances))
            min_d_key = min(dist_dict, key=dist_dict.get) 
            min_d = dist_dict.get(min_d_key)

        if min_d <= self.threshold:
            with open(self.output_search, 'w') as f:
                print('[INFO] License plate %s identified with dissimilarity of %d to be a match for %s --> ACCESS GRANTED!' % (min_d_key, min_d, plate),
                file=f)
                logger.info("License plate identified --> ACCES GRANTED!")          
        else:
            with open(self.output_search, 'w') as f:
                print('[INFO] No License plate identified with min dissimilarity of %d to be a match for %s --> ACCESS DENIED!' % (self.threshold, plate),
                file=f)
                logger.info("License plate not identified for the Whitelist --> ACCES DENIED!")    