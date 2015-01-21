#!/usr/bin/python
# -*- coding: latin-1

# Caixeta Darth Vader
# Raspberry Pi, Camera module, 2 botons, 1 buzzer extret d'un pc vell.
# Bateria per alimentar la rpi, caixa de cartró d'un paquet de llibres d'amazon, "blu-tack" per fixar rpi i bateria a la caixa.

# Boto gran  : fer foto 
# Boto petit : emetre so pel buzzer (alternant starwars Theme i starwars Imperial March)

# Executar amb sudo python darthvader.py ja que calen permisos root per accedir a GPIO
# Per executar-se al arrancar, sudo nano /etc/rc.local i afegir abans del exit(0):
# sudo python home/pi/darthvader.py &

# Infos buzzer i melodies star wars:
# http://forum.arduino.cc/index.php?topic=259450.0
# http://courses.ischool.berkeley.edu/i262/s13/content/mariespliid/lab-5-star-wars-song-selector


import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os, subprocess
import picamera

# Pins gpio on estan connectats els botons:
GPIO_PIN_BOTO_FOTO = 17
GPIO_PIN_BOTO_SO = 23
GPIO_PIN_BUZZER = 25

GPIO_PIN_CAMERA_LED = 32 # Use 5 for Model A/B and 32 for Model B+

# Paràmetres
FLIP_CAMERA = False # Donar la volta a les fotos/vídeos si la càmera està al revés

PATH_FOTOS = "/home/pi/img/"  # carpeta on es desaran les imatges, acabat amb /
FOTO_RESOLUTION = (2592, 1944)

OPCIO_FER_FOTO = 3  # 1:foto sense compte enrera.  2:Compte enrera + foto.  3:Compte enrera + n fotos consecutives.

FOTO_ESPERA = 2           # segons d'espera abans de fer la foto (si OPCIO_FER_FOTO = 1)

FOTO_COMPTE_ENRERA = 3    # segons/flashos abans de fer la foto (si OPCIO_FER_FOTO = 2)

RAFEGA_COMPTE_ENRERA = 1  # segons/flashos abans de fer la foto (si OPCIO_FER_FOTO = 3)
RAFEGA_NUM_FOTOS = 3      # quantes fotos es fan en una ràfega
RAFEGA_ESPERA = .5        # segons d'espera entre fotos d'una ràfega

# Microsegons d'espera entre clics per evitar bouncing (rebre un mateix clic vàries vegades!)
# Ajustar-ho en funció de la durada de l'acció.
BOUNCE_TIME_FOTO = 3000 + (FOTO_COMPTE_ENRERA * 1000)
BOUNCE_TIME_SO = 3000

# Buzzer
TEMPO_BEEP = 120  # 100 seria el correcte. augmentat una mica per accelerar-ho


def compte_enrera(segons):
	# pampalluguejar led de la càmera
	for n in range(0, segons):
		GPIO.output(GPIO_PIN_CAMERA_LED, False)
		time.sleep(.5)
		GPIO.output(GPIO_PIN_CAMERA_LED, True)
		time.sleep(.5)

def clic_foto(channel):
	global estat, camera

	if estat > 0:
		return # càmera en ús, retornar

	estat = 1
	camera = picamera.PiCamera()
	camera.resolution = FOTO_RESOLUTION
	if FLIP_CAMERA:
		camera.hflip = True
		camera.vflip = True

	# Selfie photo. foto sense compte enrera.
	if OPCIO_FER_FOTO == 1:
		GPIO.output(GPIO_PIN_CAMERA_LED, True)
		time.sleep(FOTO_ESPERA)
		dt = datetime.now()
		filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
		camera.capture(PATH_FOTOS+filename)
		print "Foto %s%s" % (PATH_FOTOS, filename)

	# Selfie photo. Compte enrera + foto.
	elif OPCIO_FER_FOTO == 2:
		compte_enrera(FOTO_COMPTE_ENRERA)
		dt = datetime.now()
		filename = "selfpi-%04d%02d%02d-%02d%02d%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
		camera.capture(PATH_FOTOS+filename)
		print "Foto %s%s" % (PATH_FOTOS, filename)

	# Selfie ràfega. Compte enrera + n fotos consecutives.
	elif OPCIO_FER_FOTO == 3:
		compte_enrera(RAFEGA_COMPTE_ENRERA)
		dt = datetime.now()
		for i in range(0, RAFEGA_NUM_FOTOS):
			filename = "selfpi-%04d%02d%02d-%02d%02d%02d-%02d.jpg" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, i+1)
			camera.capture(PATH_FOTOS+filename)
			print "Rafega %s%s" % (PATH_FOTOS, filename)
			GPIO.output(GPIO_PIN_CAMERA_LED, False)
			time.sleep(RAFEGA_ESPERA)
			if i < (RAFEGA_NUM_FOTOS - 1):
				GPIO.output(GPIO_PIN_CAMERA_LED, True)

	camera.close()
	estat = 0

def clic_so(channel):
	global estat, alterna

	if estat > 0:
		return # càmera en ús, retornar

	estat = 2
	if alterna == 0:
		melodia(melody_swt, beats_swt)
		alterna = 1
	else:
		melodia(melody_swim1, beats_swim1)
		melodia(melody_swim2, beats_swim2)
		melodia(melody_swim3, beats_swim3)
		melodia(melody_swim4, beats_swim4)
		#melodia(melody_swim5, beats_swim5)
		#melodia(melody_swim3, beats_swim3)
		#melodia(melody_swim4, beats_swim4)
		melodia(melody_swim6, beats_swim6)
		alterna = 0
	estat = 0


##### BUZZER

# NOTES:
c3 = 131
d3 = 147
e3 = 165
f3 = 175
g3 = 196
a3 = 220
b3 = 247
c4 = 261
d4 = 294
e4 = 329
f4 = 349
g4 = 392
g4s= 415
a4 = 440
a4s= 466
b4 = 493
c5 = 523
c5s= 554
d5 = 586
d5s= 622
e5 = 659
f5 = 698
f5s= 740
g5 = 784
g5s= 830
a5 = 880
a5s= 932
b5 = 988
c6 = 1047
R = 0

# Star Wars Theme
melody_swt = [ f4, f4, f4, a4s,  f5, d5s, d5, c5, a5s, f5, d5s,  d5,  c5, a5s, f5, d5s, d5, d5s,  c5 ]
beats_swt  = [ 21, 21, 21, 128, 128,  21, 21, 21, 128, 64,  21,  21,  21, 128, 64,  21, 21,  21, 128 ] 

# Star Wars Imperial March
melody_swim1 = [ a4, a4, a4, f4, c5, a4, f4, c5, a4, R ]
beats_swim1  = [ 50, 50, 50, 35, 15, 50, 35, 15, 65, 50 ] 

melody_swim2 = [ e5, e5, e5, f5, c5, g4s, f4, c5, a4, R ]
beats_swim2  = [ 50, 50, 50, 35, 15,  50, 35, 15, 65, 50 ] 

melody_swim3 = [ a5, a4, a4, a5, g5s, g5, f5s, f5, f5s, R ]
beats_swim3  = [ 50, 30, 15, 50, 32,  18,  13, 13, 25, 32 ] 

melody_swim4 = [ a4s, d5s, d5, c5s, c5, b4, c5,  R ]
beats_swim4  = [  25,  50, 32, 18,  12, 12, 25, 35 ] 

melody_swim5 = [ f4, g4s, f4, a4, c5, a4, c5, e5,  R ]
beats_swim5  = [ 25,  50, 35, 12, 50, 38, 12, 65, 50 ] 

melody_swim6 = [ f4, g4s, f4, c5, a4, f4, c5, a4,  R ]
beats_swim6  = [ 25,  50, 38, 12, 50, 38, 12, 65, 65 ] 


def buzz(pitch, duration):   #create the function "buzz" and feed it the pitch and duration)
	period = 1.0 / pitch   #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
	delay = period / 2     #calculate the time for half of the wave
	cycles = int(duration * pitch)   #the number of waves to produce is the duration times the frequency
	#print pitch, duration, period, delay, cycles
	for i in range(cycles):    #start a loop from 0 to the variable "cycles" calculated above
		GPIO.output(GPIO_PIN_BUZZER, True)
		time.sleep(delay)
		GPIO.output(GPIO_PIN_BUZZER, False)
		time.sleep(delay)

def beep(note, duration_cs):
	duration_s = float(duration_cs) / TEMPO_BEEP  # / 100 seria el correcte. augmentat una mica per accelerar-ho
	if note == 0:
		time.sleep(duration_s)
	else:
		buzz(note, duration_s)
	time.sleep(0.05)

def melodia(melody, beats):
	for i, m in enumerate(melody):
		#print m, beats[i]
		beep(m, beats[i])


##### MAIN

try:
	estat = 0  # 0:res  1:foto en curs  2:so en curs
	alterna = 0  # per alternar sons

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(GPIO_PIN_BUZZER, GPIO.OUT, initial=False)
	GPIO.setup(GPIO_PIN_CAMERA_LED, GPIO.OUT, initial=False)
	
	GPIO.setup(GPIO_PIN_BOTO_FOTO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_PIN_BOTO_SO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(GPIO_PIN_BOTO_FOTO, GPIO.FALLING, callback=clic_foto, bouncetime=BOUNCE_TIME_FOTO)
	GPIO.add_event_detect(GPIO_PIN_BOTO_SO, GPIO.FALLING, callback=clic_so, bouncetime=BOUNCE_TIME_SO)
	
	while True:
		time.sleep(10)

except KeyboardInterrupt:
	print ""

finally:
	GPIO.cleanup()
	if 'camera' in globals():
		camera.close()
