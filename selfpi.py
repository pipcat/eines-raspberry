#!/usr/bin/python
# -*- coding: latin-1

# SelfPi - Push button & Smile ;-)
# Selfie maker with Raspberry Pi, Camera module and one hardware button.

# Hardware button connected to pins 9 (GROUND) and 11 (GPIO17)

# Executar amb sudo python selfpi.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrancar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/selfpi.py &

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import picamera

PATH_FOTOS = "/home/pi/camera/img/"  # carpeta on es desaran les imatges, acabat amb /
CAM_RESOLUTION = (2592, 1944)

GPIO_PIN_BOTO = 17
GPIO_PIN_CAMERA_LED = 32 # Use 5 for Model A/B and 32 for Model B+

BOUNCE_TIME = 7000 # microsegons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)
# Cal ajustar-ho en funció de la durada de clic_boto()
# Ex: amb compte_enrera(segons=5) cal BOUNCE_TIME >= 7s (amb 6 a vegades va bé altres fa doble clic)


def compte_enrera(segons):
	# pampalluguejar led
	for n in range(0, segons):
		GPIO.output(GPIO_PIN_CAMERA_LED, False)
		time.sleep(.5)
		GPIO.output(GPIO_PIN_CAMERA_LED, True)
		time.sleep(.5)


def clic_boto(channel):
	global camera

	dt = datetime.now()
	filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
	print "Foto %s%s" % (PATH_FOTOS, filename)
	camera = picamera.PiCamera()
	camera.resolution = CAM_RESOLUTION
	compte_enrera(4)
	camera.capture(PATH_FOTOS+filename)
	camera.close()


# MAIN

try:
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_CAMERA_LED, GPIO.OUT, initial=False)
	GPIO.setup(GPIO_PIN_BOTO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	GPIO.add_event_detect(GPIO_PIN_BOTO, GPIO.FALLING, callback=clic_boto, bouncetime=BOUNCE_TIME)
	
	print "SelfPi activat"
	while True:
		time.sleep(10)

except KeyboardInterrupt:
	print ""

finally:
	print "SelfPi desactivat"
	GPIO.cleanup()
	if 'camera' in globals():
		camera.close()
