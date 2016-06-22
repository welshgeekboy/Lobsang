#!/usr/bin/env python
#
# Lobsang.py- custom script gathering
# all of Lobsang's basic capabilities
# into one big,  easy-to-use library.
#
# Head servo values: 
#       (-)
#        ^
#        |
# (+) <--|--> (-) 
#        |
#        v
#       (+)
#
# Created Jun 2016 by Finley Watson.

import subprocess
import os
import sys
import serial as serial_lib
import time
import RPi.GPIO as GPIO

duino_enable_pin = 4 # Pi output BCM pin to stop Duino doing anything. Duino enabled by default.

try:
	gpio_access = True
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(duino_enable_pin, GPIO.OUT)
	# IR line sensor board Pi inputs
	GPIO.setup(16, GPIO.IN)
	GPIO.setup(20, GPIO.IN)
	GPIO.setup(21, GPIO.IN)
	# Laser Pi output
	GPIO.setup(17, GPIO.OUT)
	GPIO.output(17, False)
except RuntimeError:
	print "Lobsang: Re-run with sudo prefix, access to GPIO denied."
	gpio_access = False
	raise SystemExit

# Import here to quell error raised on no IO access. try / catch above handles and exits instead (before).
import Oled as oled

class Terminalmsg():
	'''Class for printing information to the
	   terminal. Loosely models Linux boot
	   messages, in that you get coloured
	   pre-message flags, eg [ ok ] in green.'''
	def __init__(self):
		'''Runs on class initialisation. Sets
		   variables to control prompt print colour.'''
		self.OK = "\033[32m" # Bright green.
		self.INFO = "\033[36m" # Bright blue.
		self.WARNING = "\033[33m" # Bold orange.
		self.FAIL = "\033[31m" # Dark red.
		self.BOOT = "\033[35m" # Dark, bold pink.
		self.INDIGO = "\033[1;34m" # Indigo.
		self.YELLOW = "\033[1;33m" # Yellow.
		self.AUTO = "\033[0m" # Very pale grey. Automatic terminal colour.

	def printf(self, msg):
		'''Prints $msg to the terminal literally,
		   so you need to put a return at the end of
		   your string if you want to carrige return.'''
		subprocess.call(["printf", msg])
	
	def check(self, msg):
		'''Call this before ok() or fail() to print
		   a 'checking...' message, shown like:
		   [ .. ] $msg...
		   then call ok() or fail(), which will print
		   over this message to go from the above to:
		   [ ok ] $msg...done.'''
		msg = "[ .. ] " + str(msg) + "...\r"
		subprocess.call(["printf", msg])
	
	def ok(self, msg):
		'''Prints an 'ok' message to the terminal
		   with a coloured 'ok' flag before $msg.'''
		msg = "[ "+ self.OK +"ok"+ self.AUTO +" ] "+ msg +"...done."
		subprocess.call(["echo", "-e", msg])
	
	def fail(self, msg):
		'''Prints a 'failed' message to the terminal
		   with a coloured 'fail' flag before $msg.'''
		msg = "["+ self.FAIL +"fail"+ self.AUTO +"] "+ msg +"...failed!"
		subprocess.call(["echo", "-e", msg])

	def info(self, msg):
		'''Prints an 'info' message to the terminal
		   with a coloured 'info' flag before $msg.
		   Should not be used with check().'''
		msg = "["+ self.INFO +"info"+ self.AUTO +"] "+ msg
		subprocess.call(["echo", "-e", msg])

	def warning(self, msg):
		'''Prints a 'warning' message to the terminal
		   with a coloured 'warn' flag before $msg.
		   Should not be used with check().'''
		msg = "["+ self.WARNING +"warn"+ self.AUTO +"] "+ msg
		subprocess.call(["echo", "-e", msg])

	def boot(self, msg):
		'''Prints a 'boot' message to the terminal
		   with a coloured 'boot' flag before $msg.
		   Should not be used with check().'''
		msg = "["+ self.BOOT +"boot"+ self.AUTO +"] "+ msg
		subprocess.call(["echo", "-e", msg])

class Voice():
	'''Class for making Lobsang speak. Uses
	   espeak with customised voices, and
	   returns immediately, before espeak
	   has finished talking.'''
	def __init__(self):
		'''Runs on class initialisation. Sets
		   voice variables.'''
		self.NORMAL = " -v lobsang"
		self.HIGH = " -v lobsang-high"
		self.MONO = " -v lobsang-mono"
		self.DEEP = " -v lobsang-deep"
		self.CLEAR = " -v lobsang-clear"
		self.VOICE = self.NORMAL
		self.SPEED = " -s 170"
		self.VOLUME = " -a 500"
	
	def say(self, speech):
		'''Says $speech with espeak, sends any
		   stderr to a dumping-file. Returns
		   immediately (before espeak has finished).'''
		os.system("espeak"+ self.VOICE + self.SPEED + self.VOLUME +" '"+ str(speech) +" ' 2>> /tmp/espeak_info_and_data_dump &")
	
	def volume(self, volume):
		'''Sets voice volume.'''
		self.VOLUME = " -a "+ str(volume)
	
	def speed(self, speedwpm):
		'''Sets speed of talking in words per minute.'''
		self.SPEED = " -s "+ str(speedwpm)

	def voice(self, voice):
		'''Sets voice to use from selection of
		   custom predefined voices.'''
		if voice in (self.NORMAL, self.HIGH, self.MONO, self.DEEP, self.CLEAR):
			self.VOICE = voice
		else:
			print "Wrong voice selected: '%s' Will use normal voice." %voice


class Serial():
	'''Class for serial communication with Duino.'''
	def __init__(self):
		'''Prepares class. Runs on calling the class.'''
		self.duino_serial_port = serial_lib.Serial("/dev/ttyAMA0")
		self.RECEIVE = 1
		self.SEND = 1
		self.IDLE = 0
		self.state = self.IDLE

	def __enter__(self):
		return self
	
	def bytes_to_string(self, msg):
		'''Convert and return received serial bytes
		   $msg to string. If byte is not decodable,
		   return question mark (error handling).'''
		try:
			return bytes.decode(msg)
		except UnicodeDecodeError:
			return "?"
	
	def write(self, msg):
		'''Send string $msg to serial device.'''
		if self.state == self.IDLE and self.duino_serial_port.isOpen():
			self.state = self.SEND
			self.duino_serial_port.write(bytearray(msg, "ascii"))
			self.state = self.IDLE
	
	def flush(self):
		'''Ought to remove all data in serial buffer. TODO: make sure it works properly!'''
		if self.state == self.IDLE and self.duino_serial_port.isOpen():
			self.state = self.RECEIVE
			while self.duino_serial_port.inWaiting() > 0:
				self.duino_serial_port.read(1)
			self.state = self.IDLE
	
	def receive(self):
		'''Reads serial buffer in an infinite loop
		   until it finds terminating char(s) then
		   returns buffer string. WARNING: will hang
		   if terminating chars are not received as
		   timeout currectly does not work!'''
		# TODO: Sort out timeout problem
		message = ""
		terminate = "\r\n"
		timeout = 0.2
		if self.state == self.IDLE and self.duino_serial_port.isOpen():
			self.state = self.RECEIVE
			self.duino_serial_port.timeout = timeout
			while self.state == self.RECEIVE:
				echovalue = ""
				while self.duino_serial_port.inWaiting() > 0:
					echovalue += self.bytes_to_string(self.duino_serial_port.read(1))
				message += echovalue
				if terminate in message:
					self.state = self.IDLE
			return message
	
	def read(self):
		'''Reads contents of serial buffer at moment
		   of function call (doesn't wait for new data).'''
		message = ""
		timeout = 0.2
		self.duino_serial_port.timeout = timeout
		if self.state == self.IDLE and self.duino_serial_port.isOpen():
			self.state = self.RECEIVE
			while self.duino_serial_port.inWaiting() > 0:
				message += self.bytes_to_string(self.duino_serial_port.read(1))
			self.state = self.IDLE
			return message
	
	def __exit__(self, type, value, traceback):
		'''Runs on program exit or eg. KeyboardInterrupt
		   and closes the serial port.'''
		self.duino_serial_port.close()

class Duino():
	'''Gives access to Duino-specific commands.'''
	def reset(self):
		'''Equivalent to pressing RESET button on
		   an Arduino. Resets ATMega chip on Duino.
		   Program is not lost but RAM memory is.'''
		os.system("avrdude -q -q -p m328p -c gpio 2> /tmp/avrdude_duino_output_dump")
	
	def erase(self):
		'''Erases flash memory on ATMega. Program is lost,
		   ready to be replaced. Sends stderr to errors.txt.'''
		os.system("avrdude -q -q -p m328p -c gpio -P gpio -e 2> /tmp/avrdude_duino_ouput_dump")
	
	def enable(self):
		'''Switches off Pi pin 4 (BCM) -> Duino pin 2,
		   allowing Duino to change it's pin logic
		   levels (and therefore control Lobsang).'''
		GPIO.output(duino_enable_pin, False)
	
	def disable(self):
		'''Switches on Pi pin 4 (BCM) -> Duino pin 2,
		   completely disabling Duino (for safety).
		   Automaticaly stops motors too.'''
		GPIO.output(duino_enable_pin, True)
	
	def online(self):
		'''Checks if Duino is functioning. Sends "OK?"
		   to serial port and waits for "DUINO-OK" reply.
		   2 second timeout, Duino should have replied by then.'''
		serial.write("OK?")
		reply = ""
		for i in range(0, 20): # Max check time 1 second.
			time.sleep(0.05)
			reply += serial.read()
			if "DUINO-OK" in reply:
				return True
		return False
	
	def shutdown(self):
		'''Duino cannot 'shutdown' but make it work in
		   sync with the Pi shutting down- LED goes on,
		   when Pi has shutdown LED goes off then Duino
		   stops doing anything.'''
		serial.write("SHUTDOWN")
	
	def __exit__(self, type, value, traceback):
		'''No sure if I need this. The print statement
		   never runs so I don't think I do need it.'''
		print "Lobsang.Duino().__exit__() says 'program exited'."

class Wheels():
	'''Class for motor control over serial to Duino.
	   Duino does the I/O, Pi tells it what to do.'''
	def __init__(self):
		'''Runs on class initialisation. Prepares variables'''
		# Internally, speed == (0 to 32). The user uses speed == (-16 to 16) though. So here, 16 == 0 in actual motor speed terms.
		self.left_speed = 16
		self.right_speed = 16
		self.calibration = -0.4
	
	def calibrate_speeds(self, calibration):
		'''Set the calibration amount (added to right motor,
		   taken from left motor). Amount must be 3.0 to -3.0
		   (following the 16 to -16 motor speed standard used
		   here) but turns into a different value for serial
		   transmission. (+/-)3.0 is used because 
		   (cal * 16 + 49) gives a range of approx. (0 to 99)
		   so only 2 units need to be sent over serial.'''
		calibration = min(calibration, 3.0)
		calibration = max(calibration, -3.0)
		self.calibration = calibration
		calibration = int(calibration * 16)
		calibration += 49
		if calibration < 10: command = "CAL0"
		else: command = "CAL"
		serial.write(command + str(calibration))
	
	def left(self, speed, ramped=True):
		'''Set left motor speed (-16 to 16) via serial.'''
		if self.left_speed != speed: # Only tell the Duino to change the speed if the new speed not the same as the current speed.
			speed += 16
			speed = min(speed, 32)
			speed = max(speed, 0)
			self.left_speed = speed
			if ramped: control = "R"
			else: control = "I"
			if speed < 10:
				command = "LM%s0%i" %(control, speed)
			else:
				command = "LM%s%i" %(control, speed)
			serial.write(command)
	
	def right(self, speed, ramped=True):
		'''Set right motor speed (-16 to 16) via serial.'''
		if self.right_speed != speed:
			speed += 16
			speed = min(speed, 32)
			speed = max(speed, 0)
			self.right_speed = speed
			if ramped: control = "R"
			else: control = "I"
			if speed < 10:
				command = "RM%s0%i" %(control, speed)
			else:
				command = "RM%s%i" %(control, speed)
			serial.write(command)
	
	def both(self, left_speed, right_speed = "unspecified", ramped=True):
		'''Set left and right motor speeds (-16 to 16) via
		   serial. If $right_speed is not specified, both
		   motors are set to $left_speed. Otherwise, it
		   behaves like calling left() then right(), but
		   sends commands in one go not seperately.'''
		# This statement only occurs when there are two (L & R) speeds set and they are different and
		# (later on inside statement) if either or both motor speeds are different from their old speeds.
		if right_speed != "unspecified" and right_speed != left_speed:
			left_speed += 16
			right_speed += 16
			left_speed = min(left_speed, 32)
			left_speed = max(left_speed, 0)
			right_speed = min(right_speed, 32)
			right_speed = max(right_speed, 0)
			command = ""
			if ramped: control = "R"
			else: control = "I"
			if self.left_speed != left_speed:
				if left_speed < 10:
					command += "LM%s0%i" %(control, left_speed)
				else:
					command += "LM%s%i" %(control, left_speed)
			if self.right_speed != right_speed:
				if right_speed < 10:
					command += "RM%s0%i" %(control, right_speed)
				else:
					command += "RM%s%i" %(control, right_speed)
			self.left_speed = left_speed
			self.right_speed = right_speed
			#print command
			if command != "": serial.write(command)
		
		elif self.left_speed != left_speed + 16 or self.right_speed != left_speed + 16:
			left_speed += 16
			command = ""
			left_speed = min(left_speed, 32)
			left_speed = max(left_speed, 0)
			self.left_speed = left_speed
			self.right_speed = left_speed
			if ramped: control = "R"
			else: control = "I"
			if left_speed < 10:
				command += "BM%s0%i" %(control, left_speed)
			else:
				command += "BM%s%i" %(control, left_speed)
			#print command
			serial.write(command)

class Sensors():
	'''Class for accessing Lobsang's sensors, except
	   camera and line sensor, via serial with the Duino.'''
	def line_map_duino(self):
		'''Returns an array of the three IR sensor readings
		   (0 or 1) for line following- maps the line.'''
		map = [0, 0, 0]
		serial.write("IR")
		response = serial.receive()
		if response[:2] == "IR":
			map[0] = response[2]
			map[1] = response[3]
			map[2] = response[4]
			# 'map[0] = int(map[0])' doesn't work (because of ANSII encoding maybe??)
			if map[0] == "1": map[0] = 1
			else: map[0] = 0
			if map[1] == "1": map[1] = 1
			else: map[1] = 0
			if map[2] == "1": map[2] = 1
			else: map[2] = 0
			return map
		else:
			print "Lobsang.Sensors.line_map(): response[:2] != 'IR', response == '", response, "'"
			return False

	def line_map(self):
		'''Returns an array of the three IR sensor readings
		   (0 or 1) for line following- maps the line.'''
		map = [GPIO.input(21), GPIO.input(20), GPIO.input(16)]
		return map

	def distance(self):
		'''Returns distance in cm from ultrasonic sensor on head.'''
		serial.write("US?")
		response = serial.receive()
		if response[:2] == "US":
			cm = float(response[2:len(response) - 2]) # cut out the bits we don't need and convert to float
			return cm
		else:
			raise TypeError("Response from duino did not begin with 'US'.\r\nResponse was '%s'." %response)

class Head():
	def __init__(self, pan_ms, tilt_ms):
		self.pan_ms = pan_ms
		self.tilt_ms = tilt_ms
		#serial.write("PS"+ str(pan_ms) +"TS"+ str(tilt_ms))
	
	def laser(self, value):
		GPIO.output(17, value)

	def pan(self, ms):
		'''Set the angle of the pan (left/right) face servo (1000 to 2000) in ms.'''
		if ms > 2000:
			ms = 2000
		elif ms < 1000:
			ms = 1000
		serial.write("PS"+ str(ms))
		self.pan_ms = ms
	
	def tilt(self, ms):
		'''Set the angle of the tilt (up/down) face servo (1000 to 2000) in ms'''
		if ms > 2000:
			ms = 2000
		elif ms < 1000:
			ms = 1000
		serial.write("TS"+ str(ms))
		self.tilt_ms = ms
	
	def aim(self, pan_ms, tilt_ms):
		'''Set angles of pan and tilt head servos (1000 to 2000) in ms'''
		if pan_ms > 2000:
			pan_ms = 2000
		elif pan_ms < 1000:
			pan_ms = 1000
		if tilt_ms > 2000:
			tilt_ms = 2000
		elif tilt_ms < 1000:
			tilt_ms = 1000
		serial.write("PS"+ str(pan_ms) +"TS"+ str(tilt_ms))
		self.pan_ms = pan_ms
		self.tilt_ms = tilt_ms

class Appendage():
	'''Functions specific to the Pi Wars skittles challenge.
	   This class may be expanded in future (eg. for a gripper).
	   Currently, you can open and close the ball guide and
	   release the ball launching paddle.'''
	class Launcher():
		def __init__(self):
			self.guide_status = "open"
			serial.write("LAG1300")
			serial.write("LAP2000")
		
		def connect(self):
			serial.write("LAC1") # Tell Duino that the launcher is connected.
		
		def disconnect(self):
			serial.write("LAC0") # Get the Duino to disable launcher outputs.

		def open_guide(self):
			#if self.guide_status == "closed":
			serial.write("LAG1300")
			#self.guide_status = "open"
		
		def close_guide(self):
			#if self.guide_status == "open":
			serial.write("LAG1080")
			#self.guide_status = "closed"
		
		def release_paddle(self):
			serial.write("LAP1000")
		
		def reset_paddle(self):
			serial.write("LAP2000")
		
		def launch_ball(self):
			self.open_guide()
			time.sleep(0.1)
			self.release_paddle()
			#time.sleep(0.5)
			#self.close_guide()


class Msglog():
	def log(self, logstring):
		'''Adds log message to /home/pi/lobsang/memories/log/Lobsang.log'''
		fullstring = time.asctime() +" --> [ LOG ] "+ logstring +"\r\n"
		with open("/home/pi/lobsang/memories/log/Lobsang.log", "a") as logfile:
			logfile.writelines(fullstring)
		
	def error(self, errorstring):
		'''Adds error message to /home/pi/lobsang/memories/log/Lobsang.log'''
		fullstring = time.asctime() +" --> [ERROR] "+ errorstring +"\r\n"
		with open("/home/pi/lobsang/memories/log/Lobsang.log", "a") as logfile:
			logfile.writelines(fullstring)
	
	def warning(self, warnstring):
		'''Adds warning message to /home/pi/lobsang/memories/log/Lobsang.log'''
		fullstring = time.asctime() +" --> [WARN ] "+ warnstring +"\r\n"
		with open("/home/pi/lobsang/memories/log/Lobsang.log", "a") as logfile:
			logfile.writelines(fullstring)
	
	def show(self, num_lines="all", type="together"):
		with open("/home/pi/lobsang/memories/log/Lobsang.log") as logfile:
			if num_lines == "all":
				if type == "together":
					return logfile.read()
				elif type == "seperate":
					return logfile.readlines()
			elif int(num_lines):
				output_lines = logfile.readlines()
				output_lines = output_lines[len(output_lines) - num_lines:]
				if type == "together":
					temp_lines = output_lines
					output_lines = ""
					for line in temp_lines:
						output_lines += line
					return output_lines
				elif type == "seperate":
					return output_lines
	def new_log(self):
		old_path  = "/home/pi/lobsang/memories/log/Lobsang.log"
		new_path  = "/home/pi/lobsang/memories/log/Lobsang.log"
		save_path = "/home/pi/lobsang/memories/log/archive/Lobsang.log%s" %int(time.time())
		with open(old_path) as current_file:
			if len(current_file.readlines()) > 1: # Only archive current logfile if it has been written to this session. No point archiving an empty file.
				new_logfile = True
		if new_logfile:
			with open(old_path) as old_file:
				os.system("touch "+ save_path)
				with open(save_path, "w") as save_file:
					fullstring = time.asctime() +" --> [ END ] This log file was archived. A new log file is used instead.\r\n"
					save_file.writelines(old_file.read())
					save_file.writelines(fullstring)
				with open(new_path, "w") as new_file:
					fullstring = time.asctime() +" --> [BEGIN] New log file started. To review old log files, see ./archive/\r\n"
					new_file.writelines(fullstring)
def core_temperature():
	'''Returns the temperature of the Pi in degrees C
	   TODO: make it stop only printing to terminal.'''
	os.system("sudo /opt/vc/bin/vcgencmd measure_temp")

def begin(splashscreen=True):
	log.log("Lobsang.begin() called.")
	duino.disable()
	time.sleep(0.1)
	duino.enable()
	for i in range(0, 4):
		time.sleep(0.1)
		if duino.online():
			log.log("Duino responded to 'OK?' query. Duino Online.")
			break
		else:
			log.warning("Duino did not respond to 'OK?' query. Resetting...")
			duino.reset()
			time.sleep(0.5)
	if not duino.online():
		log.error("Duino is not responding to 'OK?' query. Cannot continue running program.")
		raise IOError("Duino is not responding.")
	wheels.calibrate_speeds(wheels.calibration)
	if splashscreen:
		oled.splashscreen()
		oled.refresh()

def quit(screensaver=True):
	head.aim(1430, 1200)
	head.laser(False)
	if screensaver:
		oled.clear_buffer()
		oled.write("Booted.")
		oled.refresh()
		time.sleep(0.2)
	else:
		oled.clear()
		time.sleep(0.2)
	duino.disable()

def halt():
	duino.enable()
	time.sleep(0.1)
	tries = 0
	while not duino.online() and tries < 5:
		print "Resetting..."
		duino.reset()
		time.sleep(2)
		tries += 1
	duino.shutdown()
	terminal.info("Shutting down Lobsang...")
	log.log("Halting Lobsang. Raspbian is shutting down.")
	log.new_log() # If Lobsang halted through this code (it generally does) then create a new logfile.
	oled.clear_buffer()
	oled.write("Shutting down Lobsang...", pos=(0,0))
	oled.write("Wait until Duino light goes out before switching off.", pos=(0, 24))
	oled.refresh()
	os.system("sudo halt")


# Create instances of each class.
serial   = Serial()
log      = Msglog()
terminal = Terminalmsg()
duino    = Duino()
wheels   = Wheels()
sensors  = Sensors()
voice    = Voice()
head     = Head(1500, 1300)
launcher = Appendage().Launcher()
