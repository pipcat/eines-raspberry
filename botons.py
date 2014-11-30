#!/usr/bin/python
# -*- coding: latin-1

# Gestió botons connectats al GPIO
# Raspberry Pi, Camera module and three hardware buttons.

# Executar amb sudo python botons.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrancar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/botons.py &

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os, subprocess
import picamera

PATH_FOTOS = "/home/pi/camera/img/"  # carpeta on es desaran les imatges, acabat amb /
FOTO_RESOLUTION = (2592, 1944)

PATH_VIDEOS = "/home/pi/camera/img/"  # carpeta on es desaran els vídeos, acabat amb /
VIDEO_RESOLUTION = (1024, 768)
VIDEO_FRAMERATE = 24
	# Camera modes: http://picamera.readthedocs.org/en/release-1.8/fov.html
	# 4:3 => (2592, 1944), (1296, 972), (1024, 768), (800, 600), (640, 480)
	# 16:9 => (1920, 1080), (1296, 730), (1280, 720)
	# (1024, 768) 24fps : 1 minut +/- 50mb. 1 hora +/- 3gb

GPIO_PIN_BOTO1 = 27
GPIO_PIN_BOTO2 = 17
GPIO_PIN_BOTO3 = 26
GPIO_PIN_CAMERA_LED = 32 # Use 5 for Model A/B and 32 for Model B+

BOUNCE_TIME_FOTO = 7000 # microsegons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)
# Cal ajustar-ho en funció de la durada de clic_boto()
# Ex: amb compte_enrera(segons=5) cal BOUNCE_TIME >= 7s (amb 6 a vegades va bé altres fa doble clic)
BOUNCE_TIME_VIDEO = 3000


def compte_enrera(segons):
	# pampalluguejar led
	for n in range(0, segons):
		GPIO.output(GPIO_PIN_CAMERA_LED, False)
		time.sleep(.5)
		GPIO.output(GPIO_PIN_CAMERA_LED, True)
		time.sleep(.5)

def clic_foto(channel):
	global estat, camera

	if estat > 0:
		return # hi ha vídeo en curs
	estat = 1
	dt = datetime.now()
	filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
	print "Foto %s%s" % (PATH_FOTOS, filename)
	camera = picamera.PiCamera()
	camera.resolution = FOTO_RESOLUTION
	compte_enrera(4)
	camera.capture(PATH_FOTOS+filename)
	camera.close()
	estat = 0

def clic_video(channel):
	global estat, filename, camera
	
	if estat == 1:
		return # hi ha foto en curs
	elif estat == 0:
		print "iniciant gravació"
		dt = datetime.now()
		filename = "selfvideo-%04d%02d%02d-%02d%02d%02d.h264" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
		camera = picamera.PiCamera()
		camera.resolution = VIDEO_RESOLUTION
		camera.framerate = VIDEO_FRAMERATE
		#camera.led = False
		camera.start_recording(PATH_VIDEOS+filename)
		#camera.start_recording(PATH_VIDEOS+filename, bitrate=10000000, quality=20) #bitrate 10mbps, quality(h264):10(max high) to 40 (low)
		#camera.start_recording(PATH_VIDEOS+filename, quality=20) #quality(h264):10(max high) to 40 (low)
		estat = 2
	else:
		print "aturant gravació"
		camera.stop_recording()
		camera.close()
		estat = 0
		convertir_mp4(espera=False)

# Dins clic_video no esperar pq provoca bouncing si dura gaire. En canvi al finally deixar que acabi.
def convertir_mp4(espera=False):
	global subproces
	
	# Convertir a mp4 (sudo apt-get install gpac)
	mp4filename = filename.replace('.h264','.mp4')
	cmd = "MP4Box -fps %d -add %s%s %s%s" % (VIDEO_FRAMERATE, PATH_VIDEOS, filename, PATH_VIDEOS, mp4filename)
	cmd += " && chown pi:pi %s%s" % (PATH_VIDEOS, mp4filename)
	cmd += " && rm %s%s" % (PATH_VIDEOS, filename)
	if espera == False:
		subproces = subprocess.Popen(cmd, shell=True)
	else:
		p = subprocess.call(cmd, shell=True)


# MAIN

try:
	estat = 0  # 0:res  1:foto en curs  2:vídeo en curs

	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_BOTO1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_PIN_BOTO2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_PIN_BOTO3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_PIN_CAMERA_LED, GPIO.OUT, initial=False)
	
	GPIO.add_event_detect(GPIO_PIN_BOTO2, GPIO.FALLING, callback=clic_foto, bouncetime=BOUNCE_TIME_FOTO)
	GPIO.add_event_detect(GPIO_PIN_BOTO3, GPIO.FALLING, callback=clic_video, bouncetime=BOUNCE_TIME_VIDEO)
	
	GPIO.wait_for_edge(GPIO_PIN_BOTO1, GPIO.FALLING)
	estat = 9  # apagar

except KeyboardInterrupt:
	print ""

finally:
	GPIO.cleanup()
	if estat == 2:
		camera.stop_recording()
		camera.close()
		convertir_mp4(espera=True)
	elif 'camera' in globals():
		camera.close()

	# Si hi ha algun subprocess.Popen() esperar que acabi
	if 'subproces' in globals():
		subproces.wait()

	if estat == 9:
		os.system("sudo shutdown -h now")
