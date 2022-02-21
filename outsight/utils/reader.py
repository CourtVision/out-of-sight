import pytesseract
from utils.display import debug_imshow
import logging
logger = logging.getLogger(__name__)

class PlateReader:
	"""
	Class for performing OCR on the selected location of the image
	Store the minimum and maximum rectangular aspect ratio & Tesseract options psm and model type
	values along with whether or not we are in debug mode

	Args:
	------------
		minAR:int minimum rectangular aspect ratio
		maxAR:int maximum rectangular aspect ratio

	Returns:
	------------
		None
	"""
	def __init__(self, minAR: int = 4, maxAR: int = 5, psm: int = 7, oem: int = 1, debug: bool = False):
		self.minAR = minAR
		self.maxAR = maxAR
		self.debug = debug
		self.psm = psm
		self.oem = oem

	def _build_tesseract_options(self):
			# tell Tesseract to only OCR alphanumeric characters
			alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
			options = "-c tessedit_char_whitelist={}".format(alphanumeric)
			# set the PSM mode
			options += " --psm {}".format(self.psm)
			options += " --oem {}".format(self.oem)
			options += " -l {}".format('eng')
			# return the built options string
			return options

	def runOCR(self, roi):
		"""
		Runs OCR on the selected image.

		Args:
		------------
			roi:img Image of the location to be OCRed

		Returns:
		------------
			lpText:str String of the plate found on the image
		"""
		# initialize the license plate text
		lpText = None
		if roi is not None:
			# OCR the license plate
			options = self._build_tesseract_options()
			lpText = pytesseract.image_to_string(roi, config=options)
			if self.debug:
				debug_imshow("License Plate", roi)

		# return a text of the OCR'd license plate
		logger.info("OCRing of the plate location done.")  
		print("OCRing of the plate location done.")
		return lpText