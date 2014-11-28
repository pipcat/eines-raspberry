#!/usr/bin/python
# -*- coding: latin-1

# SelfPi - Push button & Smile ;-)
# Selfie maker with Raspberry Pi, Camera module, one hardware button and optionally 2 leds.

# Hardware button connected to pins 9 (GROUND) and 11 (GPIO17)
# Green led connected to pins 14 (gnd) and 16 (gpio23)
# Red led connected to pins 18 (gpio24) and 20 (gnd)
# (each led is connected to a resistor. values depend on leds, but around 300 ohms)

# Executar amb sudo python selfpi.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrencar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/selfpi.py &

# Possibles accions amb les fotos: dropbox, twitter, facebook, servidor web, email, ...
# Preferible no fer els uploads en aquest mateix script, per no haver d'esperar a què acabin. Millor un cron que ho vagi revisant i pujant.
# Dropbox: instal·lar dropbox_uploader.sh https://github.com/andreafabrizi/Dropbox-Uploader
# Twitter: instal·lar tweepy https://github.com/tweepy/tweepy

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os, subprocess

PATH_FOTOS = "/home/pi/camera/img/"  # carpeta on es desaran les imatges, acabat amb /
CAMERA_SETTINGS = "-w 2592 -h 1944 -q 100 -t 1000 -n"  # paràmetres per raspistill

GPIO_PIN_LED1 = 23 # led Vermell
GPIO_PIN_LED2 = 24 # led Verd
GPIO_PIN_BOTO = 17 # botó

ESPERA_BOUNCING = 7 # segons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)
# Cal ajustar-ho en funció de la durada de l'acció.
# Ex: fer_foto amb -t 1000 i compte_enrera(segons=4) cal ESPERA_BOUNCING >= 7 (amb 6 a vegades va bé altres fa doble clic)


def compte_enrera(pin, segons):
	# pampalluguejar led i deixar encès
	for n in range(0,segons):
		GPIO.output(pin, 1)
		time.sleep(.5)
		GPIO.output(pin, 0)
		time.sleep(.5)
	GPIO.output(pin, 1)

def fer_foto(dt):
	GPIO.output(GPIO_PIN_LED1, 1)
	filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
	print "Foto %s%s" % (PATH_FOTOS, filename)
	compte_enrera(GPIO_PIN_LED2, 4)
	executar("raspistill %s -o %s%s" % (CAMERA_SETTINGS, PATH_FOTOS, filename), "pi")
	GPIO.output(GPIO_PIN_LED1, 0)
	GPIO.output(GPIO_PIN_LED2, 0)

	#PATH_DROPBOX = "proves/"  # dropbox_upload.sh configurat com App Folder, per tant quedarà a "Apps"/SelfPi/PATH_DROPBOX
	#executar("./dropbox_uploader.sh upload %s%s %s%s" % (PATH_FOTOS, filename, PATH_DROPBOX, filename), "pi")

def clic_boto(channel):
	global dt_accio
	
	dt_ara = datetime.now()
	if (dt_ara - dt_accio).total_seconds() < ESPERA_BOUNCING:
		return
	dt_accio = dt_ara

	fer_foto(dt_ara)


def executar(ordre, usuari=""):
	if usuari == "":
		subprocess.call(ordre, shell=True)
	else:
		# selfpi.py necessita sudo pel GPIO, però per subprocessos millor forçar usuari pi enlloc d'heretar el root
		subprocess.call('su - %s -c "%s"' % (usuari, ordre), shell=True)


# MAIN

try:
	# per controlar bouncing i no processar mateix clic vàries vegades ja que el bouncetime del add_event_detect no sembla que funcioni prou bé
	dt_accio = datetime.now() - timedelta(seconds=ESPERA_BOUNCING) # descomptats segons bouncing per no haver d'esperar durant les proves
	 
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_LED1, GPIO.OUT)
	GPIO.setup(GPIO_PIN_LED2, GPIO.OUT)
	GPIO.setup(GPIO_PIN_BOTO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	GPIO.add_event_detect(GPIO_PIN_BOTO, GPIO.FALLING, callback=clic_boto, bouncetime=ESPERA_BOUNCING*1000)
	
	print "SelfPi activat"
	while True:
		time.sleep(10)

except KeyboardInterrupt:
	print ""

finally:
	print "SelfPi desactivat"
	GPIO.cleanup()
