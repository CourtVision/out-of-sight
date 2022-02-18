# import the necessary packages
import numpy as np
from cv2 import imwrite, boundingRect, mean, rectangle
from  imutils import resize
import logging
logger = logging.getLogger(__name__)


def anonymize_pixelate(image, roi, lpCnt, outpath: str, blocks: int = 3):
	"""
	Pixalate the input image and returns it with the mask superimposed.

	Args:
	------------
		image:img original image.
		roi:img Image of the license plate
		lpCnt:array Candidate contours
		outpath:str Path to persist the anonymized image
		blocks:int The number of blocks to pixelate

	Returns:
	------------
		None. Persist anonymized image.
	"""
	image = resize(image, width=600)
	(x, y, w, h) = boundingRect(lpCnt)
	# divide the input image into NxN blocks
	(rh, rw) = roi.shape[:2]
	xSteps = np.linspace(0, rw, blocks + 1, dtype="int")
	ySteps = np.linspace(0, rh, blocks + 1, dtype="int")
	# loop over the blocks in both the x and y direction
	for i in range(1, len(ySteps)):
		for j in range(1, len(xSteps)):
			# compute the starting and ending (x, y)-coordinates
			# for the current block
			startX = xSteps[j - 1]
			startY = ySteps[i - 1]
			endX = xSteps[j]
			endY = ySteps[i]
			# extract the ROI using NumPy array slicing, compute the
			# mean of the ROI, and then draw a rectangle with the
			# mean RGB values over the ROI in the original image
			roi_an = roi[startY:endY, startX:endX]
			(B, G, R) = [int(x) for x in mean(roi_an)[:3]]
			rectangle(roi, (startX, startY), (endX, endY), (B, G, R), -1)
	# return the pixelated blurred image
	image[y:y + h, x:x + w] = roi

	logger.info("Image anonymized.")  
	print("Image anonymized.")
	
	imwrite(outpath, image)