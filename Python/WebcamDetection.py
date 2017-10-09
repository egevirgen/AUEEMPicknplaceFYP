import argparse
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import numpy as np
import imutils
cap = cv2.VideoCapture(0)    
while(1):
  try:
  	ret, frame = cap.read()
 	gray_vid = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 	denoised = cv2.GaussianBlur(gray_vid,(5,5),0)
 	thresh = cv2.threshold(denoised, 50, 255, cv2.THRESH_BINARY)[1] 
 	thresh = cv2.erode(thresh, None, iterations=2)
 	thresh = cv2.dilate(thresh, None, iterations=2)
  	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE) 
  	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        
	for c in cnts:
	# compute the center of the contour
		M = cv2.moments(c)
		if (M["m00"] == 0):
			M["m00"]=1
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		print(M["m10"])
	
	# draw the contour and center of the shape on the image
		cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
		cv2.circle(frame, (cX, cY), 7, (255, 255, 0), -1)
		cv2.putText(frame, "center", (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
 
# show the output image
  	cv2.imshow("Frame", frame)
	cv2.imshow("thresh",thresh)
  except:
	pass

  if cv2.waitKey(10)==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
