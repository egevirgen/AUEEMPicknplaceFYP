# import the necessary packages
import argparse
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
args = vars(ap.parse_args())
 
# load the image, convert it to grayscale, blur it slightly,
# and threshold it
orginal_image = cv2.imread(args["image"])
image = cv2.bitwise_not(orginal_image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (9, 9), 0)
#equ = cv2.equalizeHist(gray)
#clahe = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(8,8))
#cl1 = clahe.apply(equ)
thresh = cv2.threshold(gray, 103, 255, cv2.THRESH_BINARY)[1]
thresh = cv2.erode(thresh, None, iterations=2)
thresh = cv2.dilate(thresh, None, iterations=2)


# find contours in the thresholded image
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]
# loop over the contours
for c in cnts:
	# compute the center of the contour
	M = cv2.moments(c)
	if (M["m00"] == 0):
		M["m00"]=1
	cX = int(M["m10"] / M["m00"])
	cY = int(M["m01"] / M["m00"])
	
	# draw the contour and center of the shape on the image
	cv2.drawContours(orginal_image, [c], -1, (0, 255, 0), 2)
	cv2.circle(orginal_image, (cX, cY), 7, (0, 0, 255), -1)
	cv2.putText(orginal_image, "("+str(cX)+","+str(cY)+")", (cX-40, cY - 40),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 80, 50), 1)
        cv2.putText(orginal_image, str(M["m00"]), (cX-30, cY + 45),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 80, 50), 1)
 
	# show the image

	cv2.imshow("Image", thresh)
	cv2.imshow("Image1", gray)
	cv2.imshow("Image2", orginal_image)
	
cv2.waitKey(0)

