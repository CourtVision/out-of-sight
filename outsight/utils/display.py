from cv2 import imshow, imwrite, waitKey as WK, drawContours, putText, boundingRect, \
                boxPoints, minAreaRect, FONT_HERSHEY_SIMPLEX
import imutils
import logging
logger = logging.getLogger(__name__)


def _cleanup_text(text: str):
    """
    Strips out non-ASCII text so we can draw the text on the image using OpenCV.

    Args:
    ------------
        text (str): String to trtip non-ASCII

    Returns:
    ------------
        text (str)
	"""
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def ocrout(lpText: str, lpCnt, image, outpath: str, debug: bool = False):
    """
    Persist the original image with the superimposed recognized text and contour.

    Args:
    ------------
        image (img): Original image.
        gray (img): Grayscale original image
        lpCnt (array): Array of contour
        lpText (str): Text of the plate
        debug (bool): Mode of operation is debug

    Returns:
    ------------
        None
	"""
    if lpText is not None and lpCnt is not None:
        # fit a rotated bounding box to the license plate contour and
        # draw the bounding box on the license plate
        image = imutils.resize(image, width=600)
        box = boxPoints(minAreaRect(lpCnt))
        box = box.astype("int")
        drawContours(image, [box], -1, (0, 255, 0), 2)
        # compute a normal (unrotated) bounding box for the license
        # plate and then draw the OCR'd license plate text on the image
        (x, y, w, h) = boundingRect(lpCnt)
        putText(image, _cleanup_text(lpText), (x, y - 15), FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        # show the output ANPR image
        # print("[INFO] %s" % lpText)
        if debug:
            imshow("Output ANPR", image)
            WK(0)
        imwrite(outpath, image)
 
        logger.info("Persist the image with the superimposed plate and the recognized text.")  
        print("Persist the image with the superimposed plate and the recognized text.")

    else:
        print("No license plate found!")
        logger.info("No license plate found!")  


def debug_imshow(title: str, image, waitKey: bool = True):
    """
    Show image during debugging.

    Args:
    ------------
        title (str): Title of the image
        image (img): Image to be shown
        waitKey (bool): If the wait for key stroke to continue

    Returns:
    ------------
        None
	"""
    # show the image with the supplied title
    imshow(title, image)
	# check to see if we should wait for a keypress
    if waitKey:
        WK(0)