from cv2 import imshow, imwrite, waitKey, drawContours, putText, boundingRect, boxPoints, minAreaRect, FONT_HERSHEY_SIMPLEX


def _cleanup_text(text):
	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def ocrout(lpText, lpCnt, image, debug=False):

    if lpText is not None and lpCnt is not None:
        # fit a rotated bounding box to the license plate contour and
        # draw the bounding box on the license plate
        box = boxPoints(minAreaRect(lpCnt))
        box = box.astype("int")
        drawContours(image, [box], -1, (0, 255, 0), 2)
        # compute a normal (unrotated) bounding box for the license
        # plate and then draw the OCR'd license plate text on the image
        (x, y, w, h) = boundingRect(lpCnt)
        putText(image, _cleanup_text(lpText), (x, y - 15), FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        # show the output ANPR image
        print("[INFO] {}".format(lpText))
        if debug:
            imshow("Output ANPR", image)
        imwrite("OCRout.jpg", image)
        waitKey(0)

    else:
        print("No license plate found!")


def debug_imshow(self, title, image, waitKey=True):
    # show the image with the supplied title
    imshow(title, image)
	# check to see if we should wait for a keypress
    if waitKey:
        waitKey(0)