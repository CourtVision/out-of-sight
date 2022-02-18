# import the necessary packages
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2
from utils.display import debug_imshow
import logging
logger = logging.getLogger(__name__)


class PlateLocator:
	def __init__(self, minAR: int = 4, maxAR: int = 5, debug: bool = False):
		"""
		Store the minimum and maximum rectangular aspect ratio
		values along with whether or not we are in debug mode

		Args:
		------------
			minAR:int minimum rectangular aspect ratio
			maxAR:int maximum rectangular aspect ratio

		Returns:
		------------
			None
		"""
		self.minAR = minAR
		self.maxAR = maxAR
		self.debug = debug
	
	def run_candidates(self, image, keep: int = 5):
		"""
		Performs a blackhat morphological operation that will allow
		us to reveal dark regions (i.e., text) on light backgrounds
		difference between the closing of the input image and input image.
		(i.e., the license plate itself) keeps so many sorted license plate candidate contours

		Args:
		------------
			image:img Location of the CONFIG file.

		Returns:
		------------
			config:dict  
		"""
		image = imutils.resize(image, width=600)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
		blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKern)
		if self.debug:
			debug_imshow(title="Blackhat", image=blackhat)

		# next, find regions in the image that are light
		# closing holes in image, then threshold
		# with that we find large white rectangles 
		squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
		light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
		light = cv2.threshold(light, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
		if self.debug:
			debug_imshow(title="Light Regions", image=light)

		# compute the Scharr gradient representation of the blackhat
		# Scharr gradient will detect edges in the image and emphasize the boundaries of the characters in the license plate
		# image in the x-direction and then scale the result back to the range [0, 255]
		# The Sobel Operator is a discrete differentiation operator. It computes an approximation of the gradient of an image intensity function.
		# kernerl=-1 means 3x3.

		gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
		gradX = np.absolute(gradX)
		(minVal, maxVal) = (np.min(gradX), np.max(gradX))
		gradX = 255 * ((gradX - minVal) / (maxVal - minVal))
		gradX = gradX.astype("uint8")
		if self.debug:
			debug_imshow(title="Scharr", image=gradX)

		# blur the gradient representation, applying a closing
		# operation, and threshold the image using Otsu's method
		gradX = cv2.GaussianBlur(gradX, (5, 5), 0)
		gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKern)
		thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
		if self.debug:
			debug_imshow(title="Grad Thresh", image=thresh)

		# perform a series of erosions and dilations to clean up the
		# thresholded image
		thresh = cv2.erode(thresh, None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=2)
		if self.debug:
			debug_imshow(title="Grad Erode/Dilate", image=thresh)

		# take the bitwise AND between the threshold result and the
		# light regions of the image
		# The general usage is that you want to get a subset of an image defined by another image, typically referred to as a "mask".
		# light image serves as our mask for a bitwise-AND between the thresholded result and the light regions of the image to reveal the license plate candidates
		thresh = cv2.bitwise_and(thresh, thresh, mask=light)
		thresh = cv2.dilate(thresh, None, iterations=2)
		thresh = cv2.erode(thresh, None, iterations=1)
		if self.debug:
			debug_imshow(title="Final", image=thresh, waitKey=True)

		# find contours in the thresholded image and sort them by
		# their size in descending order, keeping only the largest ones
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		candidates = sorted(cnts, key=cv2.contourArea, reverse=True)[:keep]

		# return the list of contours
		logger.info("Searching for candidate locations done.")  
		print("Searching for candidate locations done.")
		return candidates, gray


	def run_best_candidate(self, image, gray, candidates, clearBorder:bool = False):
		"""
		Gets the best position for the license plate out of candidates if they match the aspect ratio.

		Args:
		------------
			image:img Original image.
			gray:img Grayscale original image
			candidates:array Candidate contours
			clearBorder:bool Option if to clear boarders

		Returns:
		------------
			roi:array Location of the plate
			lpCnt:array Corresponding countours
			licensePlate_col:img image of the plate
		"""
		# initialize the license plate contour and ROI
		image = imutils.resize(image, width=600)
		lpCnt = None
		roi = None
		# loop over the license plate candidate contours
		for c in candidates:
			# compute the bounding box of the contour and then use
			# the bounding box to derive the aspect ratio
			(x, y, w, h) = cv2.boundingRect(c)
			ar = w / float(h)

			# check to see if the aspect ratio is rectangular
			if ar >= self.minAR and ar <= self.maxAR:
				# store the license plate contour and extract the
				# license plate from the grayscale image and then threshold it
				lpCnt = c
				licensePlate_col = image[y:y + h, x:x + w]
				licensePlate = gray[y:y + h, x:x + w]
				roi = cv2.threshold(licensePlate, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
				
				# check to see if we should clear any foreground
				# pixels touching the border of the image
				# (which typically, not but always, indicates noise)
				if clearBorder:
					roi = clear_border(roi)
				# display any debugging information and then break
				# from the loop early since we have found the license plate region
				if self.debug:
					debug_imshow(title="License Plate", image=licensePlate)
					debug_imshow(title="ROI", image=roi, waitKey=True)
				break

		# return a 3-tuple of the license plate, ROI and the contour associated with it
		logger.info("Searching for the location done.")  
		print("Searching for the location done.")
		return (roi, lpCnt, licensePlate_col)