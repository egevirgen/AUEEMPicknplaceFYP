import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
import operator
import serial
import time
from termcolor import colored
import threading
import os
import pyrebase
import json
import PCF8591 as ADC
import Tkinter

config = {
  "apiKey": "AIzaSyB-wh6uj4JIlR4XGuCuBlm9t0cRAQzoE54",
  "authDomain": "aueemfyp.firebaseapp.com",
  "databaseURL": "https://aueemfyp.firebaseio.com",
  "storageBucket": "aueemfyp.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

#adc ayarlama
ADC.setup(0x48)

global kamera_aktif
global goruntu_isleme_aktif
global frame
global uart_read

global center_temp_x
global center_temp_y
global yuzolcumleri

global sicaklik_delay
global current

global childString
global data

global sismik_adc
global sleep

global stm_temp

sleep = False

childString = ""

kamera_aktif = "true"
goruntu_isleme_aktif = "false"

sicaklik_delay = 60
current = 0

def veri_alma() :
		global uart_read
		global kamera_aktif
		global current
		global data
		global childString
		global sleep
		global stm_temp
		
		uart_read=ser.readline()
		
		if uart_read!="" :
			if uart_read.find("STM Cevabi:")!= -1 :
				print colored(uart_read,'green')
				
			if uart_read.find("STM Cevabi: Islem basari ile tamamlandi.") != -1 :
				data = {
				"state": "not active"
				}
				childString = "Robot_Durum/Durum"	
				FirebaseDataPush()
				
			elif uart_read.find("STM Cevabi: Sistem yeniden baslatildi.") != -1 :
				data = {
				"state": "not active"
				}
				childString = "Robot_Durum/Durum"	
				FirebaseDataPush()
				data = {
				"veri": "restart"
				}
				childString = "Log/"+Timestamp()	
				FirebaseDataPush()
		
			elif uart_read == "konum_x_yerinde_fotograf" :
				kamera_aktif = "false"
				print colored("STM Cevabi: Goruntu isleme modu aktif edildi.",'green')
				
			elif uart_read.find("current_")!= -1 :
				current = uart_read.split("_")[1]
				data = {"current":current,
						"timestamp":Timestamp()}
				childString = "Robot_Durum/Durum"	
				FirebaseDataPush()
					
				if(int(current)==len(center_temp_x)):
					data={"veri":"finished"}
					childString = "Log/"+Timestamp()
					FirebaseDataPush() 
					
					childString = "Robot_Durum/Durum"
					data = {"current":"0",
							"size":"0",
							"state":"not active"}
					childString = "Robot_Durum/Durum"	
					FirebaseDataPush()
					
			elif uart_read.find("emergency") != -1 :	
					data = {"state":"emergency"}
					childString = "Robot_Durum/Durum"
					FirebaseDataPush() 
					data={"veri":"emergency"}
					childString = "Log/"+Timestamp()
					FirebaseDataPush() 
			elif uart_read.find("sismik_") != -1 :
					try:
						sismik_veri = uart_read.split("_")
						sismik_threshold = sismik_veri[2]
						sismik_adc=sismik_veri[1]
						if int(sismik_adc)>int(sismik_threshold) and not sleep:
							data = {"veri": "sismik"}
							childString = "Log/"+Timestamp()	
							FirebaseDataPush()
							SleepThread()
					except:
						pass			
			elif uart_read.find("stmtemp_") != -1 :			
					stm_temp = uart_read.split("_")[1]	
										
class ADC_Request(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
		while True:
			ser.write("sismikrq")
			time.sleep(0.5)
				

				
				

class UartReceive(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
		while True:
			veri_alma()
			
class SleepThread(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
		global sleep
		sleep = True
		time.sleep(60)
		sleep = False		
		
class SendPhoto(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
		global frame			
		cv2.imwrite("current_frame.jpg", frame)
		storage.child("images/current.jpg").put("current_frame.jpg")
			
class FirebaseDataPush(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
		try:
			global data
			global childString
			db.child(childString).update(data)
		except:
			print colored("-> Internet baglantisi kurulamadi.",'yellow')	

def Timestamp():
	timestamp = str(time.time()).replace(".","0")
	if len(timestamp) == 12 :
		timestamp = timestamp + '0'
	return timestamp				

class Raspberry_Core_Temp_Check(object):
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
		while True:
			try:
				global sicaklik_delay
				global stm_temp
				ser.write("stmsicrq")
				time.sleep(1)
				temperature = os.popen("vcgencmd measure_temp").readline()
				temperature = temperature.replace("temp=","")
				temperature = temperature.replace("'C","")
				temperature = temperature.replace("\n","") 
				
				X_temperature=ADC.temperature_convert(ADC.read(0))
				Y_temperature=ADC.temperature_convert(ADC.read(1))
				Z_temperature=ADC.temperature_convert(ADC.read(2))
				
				data = {"raspberry_sicaklik_degeri": temperature,
					"X_ekseni_surucu_sicakligi": X_temperature,
					"Y_ekseni_surucu_sicakligi": Y_temperature,
					"Z_ekseni_surucu_sicakligi": Z_temperature,
					"STM_sicaklik_degeri": stm_temp}	
				db.child("Sensor_Verileri").child(Timestamp()).update(data)
				
				data2 = {}
				if float(temperature) > 80 :
						data2["raspberry_sicaklik_degeri"]=temperature
						data2["veri"]="sicaklik"
				if float(X_temperature) > 80 :
						data2["X_ekseni_surucu_sicakligi"]=X_temperature
						data2["veri"]="sicaklik"
				if float(Y_temperature) > 80 :
						data2["Y_ekseni_surucu_sicakligi"]=Y_temperature
						data2["veri"]="sicaklik"
				if float(Z_temperature) > 80 :
						data2["Z_ekseni_surucu_sicakligi"]=Z_temperature
						data2["veri"]="sicaklik"
				if float(stm_temp) > 80 :
						data2["STM_sicaklik_degeri"]=stm_temp
						data2["veri"]="sicaklik"	
							
				db.child("Log").child(Timestamp()).update(data2)			
				
				time.sleep(sicaklik_delay)	
			except:
				pass
        
class Stream_Listener(object):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
   
        def stream_handler(message):
			try:
				global sicaklik_delay
				obj = json.dumps(message["data"]["yenileme_araligi"], indent=4)
				sicaklik_delay = int(obj)
				
			except:
				sicaklik_delay = int(message["data"])
				
	try:			
		my_stream = db.child("Yenileme_Araligi").stream(stream_handler)
	except:
		print colored("-> Internet baglantisi kurulamadi.",'yellow')	
		time.sleep(10)
		Stream_Listener()
		
class Stream_Listener_2(object):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
   
    def __init__(self, interval=1):
      
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            
        thread.start()                                  

    def run(self):
   
        def stream_handler_2(message):
			try:
				obj = json.dumps(message["data"]["Komut"], indent=4)
				if str(obj) == "emergency" :
					ser.write("acilstop")
					db.child("Komut").set({"Komut" : "completed"})
				elif str(message["data"])=="restart" :
					ser.write("resetstm")
					db.child("Komut").set({"Komut" : "completed"})
				

			except:
				if str(message["data"])=="emergency" :
					ser.write("acilstop")
					db.child("Komut").set({"Komut" : "completed"})
				elif str(message["data"])=="restart" :
					ser.write("resetstm")
					db.child("Komut").set({"Komut" : "completed"})

				
	try:			
		my_stream = db.child("Komut").stream(stream_handler_2)
		
	except:
		print colored("-> Internet baglantisi kurulamadi.",'yellow')	
	
		time.sleep(10)
		Stream_Listener_2()		

 
# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream().start()

cv2.namedWindow("Frame", cv2.WINDOW_AUTOSIZE)
#Serial init
ser = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 0.001)

Raspberry_Core_Temp_Check()
Stream_Listener()
Stream_Listener_2()
UartReceive()
ADC_Request()

		

# Image process def
def image_process(frame):
	#Grayscale
	gray_vid = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#Blur
 	denoised = cv2.medianBlur(gray_vid,5)
	#Threshold
 	thresh = cv2.adaptiveThreshold(denoised,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,5,2)
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
		
		if (M["m00"] == 0):
			pass
		elif M["m00"] > 50 :
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])

			# Draw the contour and center of the shape on the image
			cv2.drawContours(frame, [c], -1, (25, 255, 0), 1)
			cv2.circle(frame, (cX, cY), 1, (255, 255, 0), -1)
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
		
		global data
		global childString
		data = {"size": len(center_temp_x),
				"state": "active",
				"current":"0",
				"timestamp":Timestamp()}
		childString = "Robot_Durum/Durum"	
		FirebaseDataPush()	
		
		data = {"veri": "started"}
		childString = "Log/"+Timestamp()
		FirebaseDataPush()	
		
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
	global frame
	
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
		kamera_aktif = "true"
		goruntu_isleme_aktif = "false"
		print colored("-> STM yeniden baslatma talebinde bulunuldu.",'yellow')	
		
		
	elif key==ord('f'):
		if goruntu_isleme_aktif == "true" :
			print colored("-> Merkez ve Yuzolcumu degerleri STM'e gonderiliyor.",'yellow')	
			uart(center_temp_x,center_temp_y,yuzolcumleri)
			SendPhoto()
	
			
		
		
def kamera_acik() :
	global frame

	frame = vs.read()
	frame = imutils.rotate(frame,-1.5)
	frame=frame[30:470,57:561]
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
		
		
				
while True:
	if kamera_aktif == "true":
		kamera_acik()
	elif kamera_aktif == "false":
		goruntu_isleme()	  	
  	
	if clickListener() == "break" :
		break  
