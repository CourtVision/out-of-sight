# import the necessary packages
from skimage.segmentation import clear_border
import imutils
from cv2 import cvtColor, COLOR_BGR2GRAY, bilateralFilter, Canny, findContours, RETR_TREE, drawContours, \
	 			CHAIN_APPROX_SIMPLE , contourArea, arcLength, approxPolyDP, boundingRect, \
				threshold, THRESH_BINARY_INV, THRESH_OTSU
from utils.display import debug_imshow
import logging
logger = logging.getLogger(__name__)


class PlateLocator:
	def __init__(self, image, minAR: int = 4, maxAR: int = 5, debug: bool = False):
		"""
		Stores the minimum and maximum rectangular aspect ratio
		values along with whether or not we are in debug mode 
		and the original image

		Args:
		------------
			minAR (int): Minimum rectangular aspect ratio
			maxAR (int): Maximum rectangular aspect ratio
			image (img): Original image

		Returns:
		------------
			The __init__ method stores the resized version of the original image.
		"""
		self.minAR = minAR
		self.maxAR = maxAR
		self.debug = debug
		self.image = imutils.resize(image, width=600)
	

	def run_candidates(self, keep: int = 5):
		"""
		Preprocesses image (edge-preserving smoothing), finds edges and contours.
		These are then sorted by area in a descending order.

		Args:
		------------
			image (img)
			keep (int): keeps so many sorted license plate candidate contours

		Returns:
		------------
			candidates (list)  
		"""
		gray = cvtColor(self.image, COLOR_BGR2GRAY)
		if self.debug:
			debug_imshow(title="Original", image=self.image)
			debug_imshow(title="Gray", image=gray)
		
		# Edge-preserving smoothing
		# https://www.geeksforgeeks.org/python-bilateral-filtering/
		# It replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels.
		# The weights depend not only on Euclidean distance of pixels, but also on the radiometric differences
		# (e.g., range differences, such as color intensity, depth distance, etc.). This preserves sharp edges.
		# d: Diameter of each pixel neighborhood.
		# sigmaColor: The greater the value, the colors farther to each other will start to get mixed.
		# sigmaSpace: The greater its value, the more further pixels will mix together, given that their colors 
		# lie within the sigmaColor range.
		gray = bilateralFilter(gray, d=7, sigmaColor=15, sigmaSpace=15) 
		if self.debug:
			debug_imshow(title="Gray filtered", image=gray)
		
		# Any edges with intensity gradient (directional change in the intensity or color in an image) more than maxVal
		# are sure to be edges and those below minVal are sure to be non-edges, so discarded. 
		# Those who lie between these two thresholds are classified edges or non-edges based on their connectivity. 
		# If they are connected to "sure-edge" pixels, they are considered to be part of edges.
		# https://docs.opencv.org/3.4/da/d22/tutorial_py_canny.html
		edged = Canny(gray, threshold1=30, threshold2=200) 
		if self.debug:
			debug_imshow(title="Edged", image=edged)
		
		# A curve joining all the continuous points (along the boundary), having same color or intensity.
		# RETR_LIST: retrieve the contours but does not create any parent-child relationship.
		# CHAIN_APPROX_SIMPLE: remove all the redundant points on the contours detected (e.g. keep only 4).
		contours = findContours(edged.copy(), RETR_TREE, CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)
		candidates = sorted(contours, key=contourArea, reverse=True)[:keep]
		
		if self.debug:
			image = self.image.copy()
			for c in candidates:
				drawContours(image, [c], -1, (0, 255, 0), 2)	
			debug_imshow(title="Contours", image=image)
		# return the list of contours
		logger.info("Searching for candidate locations done.")  
		print("Searching for candidate locations done.")
		return candidates


	def run_best_candidate(self, candidates, clearBorder: bool = True):
		"""
		Gets the best position for the license plate out of candidates if they match the aspect ratio
		and the number of edges (4) of the poligon.

		Args:
		------------
			image (img): Original image.
			candidates (list): List of Candidate contours arrays
			clearBorder (bool): Option if to clear boarders

		Returns:
		------------
			roi (array): Location of the plate
			lpCnt (array): Corresponding countours
			licensePlate_col (img): Image of the plate
		"""
		# initialize the license plate contour and ROI
		lpCnt = None
		roi = None
		# loop over the license plate candidate contours
		for c in candidates:
			# Calculates a contour perimeter i.e. the curve length
			peri = arcLength(c, closed=True)
			# The process of approximation of a shape of contour to another shape consisting of a lesser number
			# of vertices in such a way that the distance between the contours of shapes is equal to the 
			# specified precision or lesser is called approximation of a shape of the contour.
			# https://en.wikipedia.org/wiki/Ramer–Douglas–Peucker_algorithm
			# A curve composed of line segments (which is also called a Polyline in some contexts), to a curve with fewer points.
			# The simplified curve consists of a subset of the points that defined the original curve.
			# Epsilon: specifying the approximation accuracy, i.e. maximum distance between the original curve and its approximation 
			# https://en.wikipedia.org/wiki/Hausdorff_distance & http://cgm.cs.mcgill.ca/~godfried/teaching/cg-projects/98/normand/main.html
			approx = approxPolyDP(c, epsilon=0.010 * peri, closed=True)

			# Computes the bounding box of the contour and then use
			# the bounding box to derive the aspect ratio
			(x, y, w, h) = boundingRect(approx)
			ar = w / float(h)

			# Checks to see if the aspect ratio is rectangular
			if ar >= self.minAR and ar <= self.maxAR and len(approx) == 4:
				# store the license plate contour and extract the
				# license plate from the grayscale image and then threshold it
				lpCnt = approx
				licensePlate_col = self.image[y:y + h, x:x + w]
				licensePlate = cvtColor(licensePlate_col, COLOR_BGR2GRAY) 
				licensePlate = imutils.resize(licensePlate, width=400)
				roi = licensePlate.copy()
				# roi = threshold(licensePlate, 0, 255, THRESH_BINARY_INV | THRESH_OTSU)[1]
				# check to see if we should clear any foreground
				# pixels touching the border of the image
				# (which typically, not but always, indicates noise)
				if clearBorder:
					roi = clear_border(roi)
				# display any debugging information and then break
				# from the loop early since we have found the license plate region
				#if self.debug:
				#	debug_imshow(title="License Plate", image=licensePlate)
				#	debug_imshow(title="ROI", image=roi, waitKey=True)
				break
		try:
			licensePlate
			if licensePlate.any():
				# return a 3-tuple of the license plate, ROI and the contour associated with it
				logger.info("Searching for the location done.")  
				print("Searching for the location done.")
				return (roi, lpCnt, licensePlate_col)
		except NameError:
			licensePlate = None
			logger.info("Searching for the location done. No license plate found.")  
			print("Searching for the location done. No license plate found.")
			return (None, None, None)