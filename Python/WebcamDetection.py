import argparse
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import numpy as np
import imutils

# Camera init
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,360)

# Image process def
def image_process(frame):
	#Grayscale
	gray_vid = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#Blur
 	denoised = cv2.medianBlur(gray_vid,5)
	#Threshold
 	thresh = cv2.threshold(denoised, 45, 255, cv2.THRESH_BINARY)[1] 
 	thresh = cv2.erode(thresh, None, iterations=2)
 	thresh = cv2.dilate(thresh, None, iterations=2)

	return thresh;

# Contour def
def find_contours(frame_thresh):
	#Contour detection
        cnts = cv2.findContours(frame_thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE) 
  	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	for c in cnts:
		# Compute the center of the contour
		M = cv2.moments(c)
		if (M["m00"] == 0):
			M["m00"]=1
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])

		# Find the smallest bounding rectangle of each contour
		x,y,w,h = cv2.boundingRect(c)
		
		# Draw the contour and center of the shape on the image
		cv2.drawContours(frame, [c], -1, (255, 255, 0), 2)
		cv2.circle(frame, (cX, cY), 7, (255, 255, 0), -1)	
		cv2.putText(frame, "center", (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
		
		#cv2.circle(frame, (x+w, y+h), 7, (255, 0, 255), -1)	
		#cv2.circle(frame, (x, y), 7, (255, 0, 255), -1)
	return;


while(1):
 try:
        # Capture webcam frame
  	ret, frame = cap.read()

	find_contours(image_process(frame))
  		
	# Show the output image
  	cv2.imshow("Frame", frame)
 except:
	pass

	if cv2.waitKey(10)==ord('q'):
        	break

 
cap.release()
cv2.destroyAllWindows()

  
