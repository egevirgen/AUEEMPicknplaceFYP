import argparse
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import numpy as np
import imutils
import operator
import serial

# Camera init
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,360)

center_sayisi=0;
center_memory=0;
center_koordinatlari_x=[]
center_koordinatlari_y=[]

#Serial init
#ser = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 1)


# Image process def
def image_process(frame):
	#Grayscale
	gray_vid = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#Blur
 	denoised = cv2.medianBlur(gray_vid,5)
	#Threshold
 	thresh = cv2.threshold(denoised, 50, 255, cv2.THRESH_BINARY)[1] 
 	thresh = cv2.erode(thresh, None, iterations=2)
 	thresh = cv2.dilate(thresh, None, iterations=2)

	return thresh;

# Contour def
def find_contours(frame_thresh):

	center_sayisi=0
	center_koordinatlari_x=[]
	center_koordinatlari_y=[]

	#Contour detection
        cnts = cv2.findContours(frame_thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE) 
  	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	for c in cnts:
		# Compute the center of the contour
		M = cv2.moments(c)

		# Find the smallest bounding rectangle of each contour
		x,y,w,h = cv2.boundingRect(c)

		if (M["m00"] == 0):
			pass
		else :
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])

			# Draw the contour and center of the shape on the image
			cv2.drawContours(frame, [c], -1, (255, 255, 0), 2)
			cv2.circle(frame, (cX, cY), 7, (255, 255, 0), -1)	
			cv2.putText(frame, "center", (cX - 20, cY - 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

			# Sekil okunabilir halde ise center noktasini al			
			if x+w<630 and x>10 and y>10 and y+h<350 :
				center_sayisi=center_sayisi+1
				center_koordinatlari_x.append(x)
				center_koordinatlari_y.append(y)
			
	return center_sayisi,center_koordinatlari_x,center_koordinatlari_y;

#Karar mekanizmasi
def karar(center_temp_x,center_temp_y) :
	index, value = max(enumerate(center_temp_x), key=operator.itemgetter(1))				
 	return center_temp_x[index],center_temp_y[index]

#Veri gönderme
def uart(center_temp,center_memory,center_temp_x,center_temp_y) :
	if center_temp > center_memory :
		l = []
		x,y=karar(center_temp_x,center_temp_y)
		if x<100 and x>9 :
			x='0'+str(x)
		elif x<10 :
			x='00'+str(x)
		if y<100 and y>9 :
			y='0'+str(y)
		elif y<10 :
			y='00'+str(y)
		x=str(x)
		y=str(y)
		x+='a'
		x+=y
		x+='k'
		return x
while(1):
 
        # Capture webcam frame
  	ret, frame = cap.read()
	center_temp,center_temp_x,center_temp_y = find_contours(image_process(frame))
	#ser.write(uart.encode('utf-8'))
	center_memory=center_temp
	# Show the output image
  	cv2.imshow("Frame", frame)


	if cv2.waitKey(10)==ord('q'):
        	break

 
cap.release()
cv2.destroyAllWindows()

  
