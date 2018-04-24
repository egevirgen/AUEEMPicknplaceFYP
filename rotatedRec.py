# import the necessary packages
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
from pyzbar.pyzbar import decode
import argparse
import imutils
import cv2
import numpy as np
import datetime
import math
import threading


reference = {}
reference[0]=1
reference[1]=0

global gray
global qr_data_global
global camera
global image

camera = cv2.VideoCapture(0)
qr_data_global = []
gray = []
image = []

class QR_Decode(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
		while True:
			global gray
			global qr_data_global
			try:
				qr_data = decode((gray.tostring(), 160, 120))
				if qr_data != [] :
					qr_data_global = qr_data
				else :
					qr_data_global = []	
			except:
				qr_data_global = []
	
class Frame_Read(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
		while True:
			global gray
			global thresh_neg
			global camera
			global image
			
			(grabbed, frame) = camera.read()
			image = imutils.resize(frame, width=160, height=120)
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			blurred = cv2.medianBlur(gray, 5)
			thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
				cv2.THRESH_BINARY,5,2)
			thresh_neg = cv2.bitwise_not(thresh)

Frame_Read()				
QR_Decode()
# keep looping
while True:
        
        if qr_data_global != [] :
			qr_data_local=qr_data_global
			
			print "----------------------------------------------------------------------------------------------------------------------------------------------"
			qr_data_local = str(qr_data_local).replace("[Decoded(data=","")
			qr_data_local = str(qr_data_local).replace("type=","")
			qr_data_local = str(qr_data_local).replace("rect=Rect(left=","")
			qr_data_local = str(qr_data_local).replace("top=","")
			qr_data_local = str(qr_data_local).replace("width=","")
			qr_data_local = str(qr_data_local).replace("height=","")
			qr_data_local = str(qr_data_local).replace("))]","")
			qr_split = qr_data_local.split(",")
			qr_id = qr_split[0].strip()

			# find contours in the thresholded image
			cnts = cv2.findContours(thresh_neg.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)
			cnts = cnts[0] if imutils.is_cv2() else cnts[1]

			# loop over the contours
			counter=0
			for c in cnts:

									# compute the center of the contour
							M = cv2.moments(c)
							if M["m00"] > 0:
								x = int(qr_split[2]) + int(qr_split[4])/2
								y = int(qr_split[3]) + int(qr_split[5])/2
								
								rotRect = cv2.minAreaRect(c)
								box = cv2.boxPoints(rotRect)
								box = np.int0(box)
								edge1 = {}
								edge2 = {}
								selectedEdge = {}
								edge1Norm = math.sqrt((box[1][0]-box[0][0])**2 + (box[1][1]-box[0][1])**2)
								edge1[0] = box[1][0]-box[0][0]
								edge1[1] = box[1][1]-box[0][1]
								edge2Norm = math.sqrt((box[2][0]-box[1][0])**2 + (box[2][1]-box[1][1])**2)
								edge2[0] = box[2][0]-box[1][0]
								edge2[1] = box[2][1]-box[1][1]
								
								selectedEdgeNorm = edge1Norm
								selectedEdge[0] = edge1[0]
								selectedEdge[1] = edge1[1]
								if edge2Norm>edge1Norm:
									selectedEdgeNorm = edge2Norm
									selectedEdge[0] = edge2[0]
									selectedEdge[1] = edge2[1]
								
								angle = 180/math.pi * math.acos((reference[0]*selectedEdge[0] + reference[1]*selectedEdge[1]) / ((math.sqrt((reference[0])**2 + (reference[1])**2)) * selectedEdgeNorm))
								
								cv2.drawContours(image,[box],0,(0,0,255),2)
								
								cX = int(M["m10"] / M["m00"])
								cY = int(M["m01"] / M["m00"])						
																
								counter=counter+1
								now = datetime.datetime.now()
								print "QR Angle = ",angle,"QR ID = ",qr_id,"Center X = ",x,"Center Y = ",y , now

								
	try:							
		cv2.imshow("Frame", image)
	except:
		pass
	key = cv2.waitKey(1) & 0xFF

		# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
			break        # show the image



# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

