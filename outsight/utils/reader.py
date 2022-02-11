import pytesseract
from utils.display import debug_imshow

class PlateReader:
	def __init__(self, minAR=4, maxAR=5, psm=7, oem=2, debug=False):
		# store the minimum and maximum rectangular aspect ratio
		# values along with whether or not we are in debug mode
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
			# return the built options string
			return options

	def runOCR(self, roi):
		# initialize the license plate text
		lpText = None
		if roi is not None:
			# OCR the license plate
			options = self._build_tesseract_options()
			lpText = pytesseract.image_to_string(roi, config=options)
			if self.debug:
				debug_imshow("License Plate", roi)
		# return a 2-tuple of the OCR'd license plate text along with
		# the contour associated with the license plate region
		return lpText