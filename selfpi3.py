#!/usr/bin/python
# -*- coding: latin-1

# SelfPi - Push button & Smile ;-)
# Selfie maker with Raspberry Pi, Camera module, one hardware button and optionally one led and or buzzer.

# Hardware button connected to pins 9 (GROUND) and 11 (GPIO17)
# Led connected to pins 18 (gpio24) and 20 (gnd)
# (led is connected to a resistor. values depend on leds, but around 300 ohms)
# Buzzer connected to pins 16 (gpio24) and 14 (gnd)

# Executar amb sudo python selfpi.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrancar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/selfpi3.py &

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import picamera

PATH_FOTOS = "/home/pi/camera/img/"  # carpeta on es desaran les imatges, acabat amb /
CAM_RESOLUTION = (2592, 1944)

GPIO_PIN_BOTO = 17
GPIO_PIN_LED = 24
GPIO_PIN_BUZZER = 23

BOUNCE_TIME = 7000 # microsegons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)
# Cal ajustar-ho en funció de la durada de clic_boto() i compte_enrera()


def fer_beep():
	durada = .0005
	vegades = 50
	for i in range(0, vegades):
		GPIO.output(GPIO_PIN_BUZZER, 1)
		time.sleep(durada)
		GPIO.output(GPIO_PIN_BUZZER, 0)
		time.sleep(durada)

def compte_enrera():
	# avís sonor i visual. Beeps al buzzer i pampalluguejar led
	for i in range(0, 20):
		fer_beep()
		durada = .5 - (i * .035)
		if durada < 0:
			durada = 0
		time.sleep(durada)
		if i % 2 == 0:
			GPIO.output(GPIO_PIN_LED, 1)
		else:
			GPIO.output(GPIO_PIN_LED, 0)


def clic_boto(channel):
	global camera

	dt = datetime.now()
	filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
	print "Foto %s%s" % (PATH_FOTOS, filename)
	camera = picamera.PiCamera()
	camera.resolution = CAM_RESOLUTION
	compte_enrera()
	camera.capture(PATH_FOTOS+filename)
	camera.close()


# MAIN

try:
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_LED, GPIO.OUT)
	GPIO.setup(GPIO_PIN_BUZZER, GPIO.OUT)
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
