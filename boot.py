#!/usr/bin/env python
#
# boot.py- checks if the RasPiO Duino,
# RasPiCam and OLED are all connected.
# Returns a sys.exit() code  depending
# on what errors occurs.  0 on all ok.
#
# Created Nov 2015 by Finley Watson

import Lobsang
import sys

Lobsang.begin(0)

if not Lobsang.gpio_access:
	sys.exit(16)

import subprocess
import os
from time import sleep
import RPi.GPIO as GPIO

number_of_offline_systems = 0
binary_offline_flag = 0 # 0b001 (1) == duino offline, 0b011 (3) == oled and duino offline, 0b100 (4) == camera offline etc

oled_offline = False
duino_offline = False
camera_offline = False

Lobsang.duino.enable()

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, False)

Lobsang.terminal.info("Checking Lobsang's systems")

Lobsang.terminal.check("Testing RasPiO Duino")

if Lobsang.duino.online():
	Lobsang.terminal.ok("Testing RasPiO Duino")
else:
	reply = ""
	duino_online = False
	Lobsang.duino.reset()
	sleep(0.1)
	Lobsang.serial.write("OK?")
	for i in range(0, 20):
		reply += Lobsang.serial.read()
		if "DUINO-OK" in reply:
			Lobsang.terminal.ok("Testing RasPiO Duino")
			Lobsang.terminal.info("Had to reset Duino to get response.")
			duino_online = True
			break
	if not duino_online:
		Lobsang.terminal.fail("Testing RasPiO Duino")
		Lobsang.terminal.check("Checking RasPiO Duino with avrdude...")
		duino_offline = os.system("sudo avrdude -q -q -p m328p -c gpio -P gpio 2> /tmp/boot_dump")
		if duino_offline == 0 and reply == "":
			Lobsang.terminal.warning("Duino connected, but core.ino may not be uploaded! Duino is not responding.")
		elif duino_offline == 0 and reply != "":
			Lobsang.terminal.warning("Duino connected but is not responding correctly. Received: '%s'" %reply)
		elif duino_offline != 0:
			Lobsang.terminal.fail("Checking RasPiO Duino with avrdude")
			Lobsang.terminal.warning("Duino either not connected or not functioning")
			print "avrdude: Exited with code %i." %duino_offline
		Lobsang.terminal.info("Check /tmp/boot_dump for more information.")
		duino_offline = True
		number_of_offline_systems += 1


Lobsang.terminal.check("Testing OLED display")
try:
	Lobsang.oled.command(Lobsang.oled.on)
except IOError:
	oled_offline = True
finally:
	if oled_offline:
		Lobsang.terminal.fail("Testing OLED display")
		print "Check wiring?"
		number_of_offline_systems += 1
	else:
		Lobsang.terminal.ok("Testing OLED display")


Lobsang.terminal.check("Testing RasPiCam")
camera_offline = os.system("raspistill -t 1 2> /tmp/boot_dump")
if camera_offline == 0:
	Lobsang.terminal.ok("Testing RasPiCam")
else:
	Lobsang.terminal.fail("Testing RasPiCam")
	Lobsang.terminal.warning("Camera ribbon cable may be disconnected")
	camera_offline = True
	number_of_offline_systems += 1

if number_of_offline_systems == 0:
	Lobsang.terminal.boot("Lobsang booted successfully. All systems online.")
else:
	if number_of_offline_systems == 1:
		error_plural_singular = " error."
	else:
		error_plural_singular = " errors."
	Lobsang.terminal.boot("Lobsang did not boot fully: "+ str(number_of_offline_systems) + error_plural_singular)
	
	if duino_offline:
		binary_offline_flag += 1
		Lobsang.terminal.warning("Duino offline")
	if oled_offline:
		binary_offline_flag += 2
		Lobsang.terminal.warning("OLED display offline")
	if camera_offline:
		binary_offline_flag += 4
		Lobsang.terminal.warning("Camera offline")

sys.exit(binary_offline_flag)

