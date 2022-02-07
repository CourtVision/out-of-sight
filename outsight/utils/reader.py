import pytesseract
from display import debug_imshow

class OCR:
	def __init__(self, minAR=4, maxAR=5, debug=False):
		# store the minimum and maximum rectangular aspect ratio
		# values along with whether or not we are in debug mode
		self.minAR = minAR
		self.maxAR = maxAR
		self.debug = debug

	def _build_tesseract_options(self, psm=7, oem=2):
			# tell Tesseract to only OCR alphanumeric characters
			alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
			options = "-c tessedit_char_whitelist={}".format(alphanumeric)
			# set the PSM mode
			options += " --psm {}".format(psm)
			options += " --oem {}".format(oem)
			# return the built options string
			return options

	def run(self, lp, lpCnt, psm=7, oem=2):
		# initialize the license plate text
		lpText = None
		if lp is not None:
			# OCR the license plate
			options = self._build_tesseract_options(psm=psm, oem=oem)
			lpText = pytesseract.image_to_string(lp, config=options)
			if self.debug:
				debug_imshow("License Plate", lp)
		# return a 2-tuple of the OCR'd license plate text along with
		# the contour associated with the license plate region
		return (lpText, lpCnt)	