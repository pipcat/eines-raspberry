#!/usr/bin/python
# -*- coding: latin-1

# SelfVideo - Push button & Start/Stop video recording
# Raspberry Pi, Camera module and one hardware button.

# Hardware button connected to pins 9 (GROUND) and 11 (GPIO17)

# Executar amb sudo python selfvideo.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrancar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/selfvideo.py &

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import subprocess
import picamera

PATH_FOTOS = "/home/pi/camera/img/"  # carpeta on es desaran els vídeos, acabat amb /
CAM_RESOLUTION = (1024, 768)
CAM_FRAMERATE = 24
	# Camera modes: http://picamera.readthedocs.org/en/release-1.8/fov.html
	# 4:3 => (2592, 1944), (1296, 972), (1024, 768), (800, 600), (640, 480)
	# 16:9 => (1920, 1080), (1296, 730), (1280, 720)
	# (1024, 768) 24fps : 1 minut +/- 50mb. 1 hora +/- 3gb

GPIO_PIN_BOTO = 17

ESPERA_BOUNCING = 3 # segons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)


def clic_boto(channel):
	global estat, filename, camera
	
	if estat == 0:
		print "iniciant gravació"
		dt = datetime.now()
		filename = "selfvideo-%04d%02d%02d-%02d%02d%02d.h264" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
		camera = picamera.PiCamera()
		camera.resolution = CAM_RESOLUTION
		camera.framerate = CAM_FRAMERATE
		#camera.led = False
		camera.start_recording(PATH_FOTOS+filename)
		#camera.start_recording(PATH_FOTOS+filename, bitrate=10000000, quality=20) #bitrate 10mbps, quality(h264):10(max high) to 40 (low)
		#camera.start_recording(PATH_FOTOS+filename, quality=20) #quality(h264):10(max high) to 40 (low)
		estat = 1
	else:
		print "aturant gravació"
		camera.stop_recording()
		camera.close()
		estat = 0
		convertir_mp4(espera=False)


# Dins clic_boto no esperar pq provoca bouncing si dura gaire. En canvi al finally deixar que acabi.
def convertir_mp4(espera=False):
	global subproces
	
	# Convertir a mp4 (sudo apt-get install gpac)
	mp4filename = filename.replace('.h264','.mp4')
	cmd = "MP4Box -fps %d -add %s%s %s%s" % (CAM_FRAMERATE, PATH_FOTOS, filename, PATH_FOTOS, mp4filename)
	cmd += " && chown pi:pi %s%s" % (PATH_FOTOS, mp4filename)
	cmd += " && rm %s%s" % (PATH_FOTOS, filename)
	if espera == False:
		subproces = subprocess.Popen(cmd, shell=True)
	else:
		p = subprocess.call(cmd, shell=True)


# MAIN

try:
	estat = 0
	 
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_BOTO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	GPIO.add_event_detect(GPIO_PIN_BOTO, GPIO.FALLING, callback=clic_boto, bouncetime=ESPERA_BOUNCING*1000)
	
	print "SelfVideo activat"
	while True:
		time.sleep(10)

except KeyboardInterrupt:
	print ""

finally:
	print "SelfVideo desactivat"
	GPIO.cleanup()
	if estat == 1:
		camera.stop_recording()
		camera.close()
		convertir_mp4(espera=True)
	elif 'camera' in globals():
		camera.close()

	# Si hi ha algun subprocess.Popen() esperar que acabi
	if 'subproces' in globals():
		subproces.wait()
