# import the necessary packages
from skimage.segmentation import clear_border
import pytesseract
import numpy as np
import imutils
import cv2


class PyImageSearchANPR:
	def __init__(self, minAR=4, maxAR=5, debug=False):
		# store the minimum and maximum rectangular aspect ratio
		# values along with whether or not we are in debug mode
		self.minAR = minAR
		self.maxAR = maxAR
		self.debug = debug