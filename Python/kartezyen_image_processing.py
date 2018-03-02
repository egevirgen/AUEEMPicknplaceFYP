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
from termcolor import colored


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
			cv2.drawContours(frame, [c], -1, (25, 255, 0), 1)
			cv2.circle(frame, (cX, cY), 2, (255, 255, 0), -1)
			cv2.putText(frame, "", (cX - 20, cY - 20),
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
	
		ser.write("u__aktif")
		
		size_array=str(len(center_temp_x))
		if len(str(len(center_temp_x))) <  4 :
					size_temp=""
					for temp5 in range(4-len(str(len(center_temp_x)))) :
							size_temp+="0"
						
					size_array="size"+size_temp+size_array
		ser.write(size_array)
		
		for temp in range(len(center_temp_x)) :
			x=center_temp_x[temp]
			y=center_temp_y[temp]
			z=int(yuzolcumleri_temp[temp])
			if len(str(x)) < 3 :
				x_temp=""
				for temp2 in range(3-len(str(x))) :
					x_temp+="0"
				
				x = str(x_temp) + str(x)
			
			if len(str(y)) < 3 :
				y_temp=""
				for temp3 in range(3-len(str(y))) :
					y_temp+="0"
						
				y = str(y_temp) + str(y)
				
			if len(str(z)) < 6 :
				z_temp=""
				for temp4 in range(6-len(str(z))) :
					z_temp= str(z_temp)+"0"
			
				z = str(z_temp) + str(z)

			x=str(x)
			y=str(y)
			z=str(z)
			
			sonuc= x + 'a' +y +'k'
			
			sonuc2 = 'y' + z +'z'
			ser.write(sonuc)
			ser.write(sonuc2)
			
		if kamera_aktif == "false":
			kamera_aktif = "true"
			goruntu_isleme_aktif = "false"
				
		ser.write("u__pasif")	
		
	
		
def clickListener() :
	global kamera_aktif
	global goruntu_isleme_aktif
	
	key=cv2.waitKey(1) & 0xFF
	
	if key==ord('q'):
		return "break"
	
	elif key==ord('a'):
		if kamera_aktif == "true":
			ser.write("konum__x")
			print colored("-> Goruntu isleme talebinde bulunuldu.",'yellow')	
			
		elif kamera_aktif == "false":
			kamera_aktif = "true"
			goruntu_isleme_aktif = "false"
			print colored("-> Goruntu isleme modu devre disi birakildi.",'yellow')	
			
	elif key==ord('s'):
		ser.write("camplace")
		print colored("-> Fotograf cekme konumuna gitme talebinde bulunuldu.",'yellow')
		
	elif key==ord('r'):
		ser.write("resetstm")
		print colored("-> STM yeniden baslatma talebinde bulunuldu.",'yellow')	
		
	elif key==ord('f'):
		if goruntu_isleme_aktif == "true" :
			print colored("-> Merkez ve Yuzolcumu degerleri STM'e gonderiliyor.",'yellow')	
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
			if uart_read.find("STM Cevabi:")!= -1 :
				print colored(uart_read,'green')
				
			if uart_read == "konum_x_yerinde_fotograf" :
				kamera_aktif = "false"
				print colored("STM Cevabi: Goruntu isleme modu aktif edildi.",'green')
				
				
				
		
				
while True:
	if kamera_aktif == "true":
		kamera_acik()
	elif kamera_aktif == "false":
		goruntu_isleme()	
	
  	veri_alma()
  	
  	
	if clickListener() == "break" :
		break  

