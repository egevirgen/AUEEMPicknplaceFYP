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
 	thresh = cv2.threshold(denoised, 45, 255, cv2.THRESH_BINARY)[1]
 	thresh = cv2.erode(thresh, None, iterations=2)
 	thresh = cv2.dilate(thresh, None, iterations=2)
  	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_NONE)
  	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        
	for c in cnts:
		c = max(cnts, key=cv2.contourArea)
 		extLeft = tuple(c[c[:, :, 0].argmin()][0])
  		extRight = tuple(c[c[:, :, 0].argmax()][0])
  		extTop = tuple(c[c[:, :, 1].argmin()][0])
  		extBot = tuple(c[c[:, :, 1].argmax()][0])
  		cv2.drawContours(frame, [c], -1, (0, 255, 255), 2)
  		cv2.circle(frame, extLeft, 8, (0, 0, 255), -1)
  		cv2.circle(frame, extRight, 8, (0, 255, 0), -1)
  		cv2.circle(frame, extTop, 8, (255, 0, 0), -1)
  		cv2.circle(frame, extBot, 8, (255, 255, 0), -1)
  		extCenter = ((extRight[0]+extLeft[0])/2,(extBot[1]+extTop[1])/2)
  		cv2.putText(frame, "center_4kenar", (extCenter[0]-20,extCenter[1]-20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
 		cv2.circle(frame, extCenter, 8, (255, 255, 0), -1)
# show the output image
  	cv2.imshow("Frame", frame)
  except:
	pass

  
  
  if cv2.waitKey(10)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
