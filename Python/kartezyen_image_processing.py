import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import operator
import serial
import time
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())
 
# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(1.0)

cv2.namedWindow("Frame", cv2.WINDOW_AUTOSIZE)
#Serial init
ser = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 0.001)

global kamera_aktif
global goruntu_isleme_aktif
global frame
global uart_read

global center_temp_x
global center_temp_y
global yuzolcumleri


kamera_aktif = "true"
goruntu_isleme_aktif = "false"

# Image process def
def image_process(frame):
	#Grayscale
	gray_vid = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#Blur
 	denoised = cv2.medianBlur(gray_vid,5)
	#Threshold
 	thresh = cv2.adaptiveThreshold(denoised,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
 	thresh = cv2.erode(thresh, None, iterations=2)
 	thresh = cv2.dilate(thresh, None, iterations=2)
	thresh = cv2.bitwise_not(thresh)
	return thresh;

# Contour def
def find_contours(frame_thresh):

	center_koordinatlari_x=[]
	center_koordinatlari_y=[]
	yuzolcumleri=[]

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
		elif M["m00"] > 50 :
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])

			# Draw the contour and center of the shape on the image
			cv2.drawContours(frame, [c], -1, (255, 255, 0), 1)
			cv2.circle(frame, (cX, cY), 2, (255, 255, 0), -1)
			cv2.putText(frame, "center", (cX - 20, cY - 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

			# Sekil okunabilir halde ise center noktasini al
			center_koordinatlari_x.append(cX)
			center_koordinatlari_y.append(cY)
			yuzolcumleri.append(M["m00"])

	return center_koordinatlari_x,center_koordinatlari_y,yuzolcumleri;

#Veri gonderme
def uart(center_temp_x,center_temp_y,yuzolcumleri_temp) :
		global kamera_aktif
		global goruntu_isleme_aktif
	
		for temp in range(len(center_temp_x)) :
			x=center_temp_x[temp]
			y=center_temp_y[temp]
			#z=yuzolcumleri_temp[temp]
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
			sonuc= x + 'a'
			sonuc+=y
			sonuc+='k'
			#return sonuc+'-'+str(z)
			ser.write(sonuc)
			
		print("Koordinatlar STM'e gonderildi.")	
		
		if kamera_aktif == "false":
			kamera_aktif = "true"
			goruntu_isleme_aktif = "false"		
		
def clickListener() :
	global kamera_aktif
	global goruntu_isleme_aktif
	
	key=cv2.waitKey(1) & 0xFF
	
	if key==ord('q'):
		return "break"
	
	elif key==ord('a'):
		if kamera_aktif == "true":
			ser.write("konum__x")
			
		elif kamera_aktif == "false":
			kamera_aktif = "true"
			goruntu_isleme_aktif = "false"
			print("Goruntu isleme modu devre disi birakildi.")	
			
	elif key==ord('s'):
		ser.write("camplace")
		print("Platform fotograf cekme konumuna gonderiliyor...")
		
	elif key==ord('r'):
		ser.write("resetstm")
		print("STM yeniden baslatildi.")	
		
	elif key==ord('f'):
		if goruntu_isleme_aktif == "true" :
			uart(center_temp_x,center_temp_y,yuzolcumleri)			
		

def kamera_acik() :
	global frame
	
	frame = vs.read()
	frame = frame[25:440, 110:580]
	cv2.imshow("Frame", frame)		
	
	
def goruntu_isleme() :
		global frame 
		global goruntu_isleme_aktif
	
		global center_temp_x
		global center_temp_y
		global yuzolcumleri
	
		if goruntu_isleme_aktif == "false" :
			center_temp_x,center_temp_y,yuzolcumleri = find_contours(image_process(frame))	
			cv2.imshow("Frame", frame)
			goruntu_isleme_aktif = "true"
			

def veri_alma() :
		global uart_read
		global kamera_aktif
		
		uart_read=ser.readline()
		
		if uart_read!="" :
			
			if uart_read == "konum_x_yerinde_fotograf" :
				kamera_aktif = "false"
				print("Goruntu isleme modu aktif edildi.")
				
		
				
while True:
	if kamera_aktif == "true":
		kamera_acik()
	elif kamera_aktif == "false":
		goruntu_isleme()	
	
  	veri_alma()
  	
  	
	if clickListener() == "break" :
		break  

