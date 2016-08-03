#!/usr/bin/env python
#
# manual_control.py-  script to allow the user to
# control the robot with the "W A S D" keys. Uses
# pygame to get key presses,  and allows  keys to
# be pressed at the same time for greater control
# so you can drive left,  left and forward,  only
# forward, right and forward etc.  ESC  to  quit.
#
# Created Aug 2016 by Finley Watson.

print "Manual Control: Initialising."

# Import all the libraries we need.
import Lobsang
import sys
import time
import picamera.camera
import pygame
from pygame.locals import *

# Give feedback on the oled.
Lobsang.oled.write("Starting Manual Control.")
Lobsang.oled.refresh()
Lobsang.begin(splashscreen=False)

# All the variables needed.
loops_per_second = 50
left_motor_speed = 0
right_motor_speed = 0

forward = False
backward = False
left = False
right = False

pos = (0, 0)
old_pos = (0, 0)

laser_state = False

# Set up pygame
pygame.init()
DISPLAYSURF = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Lobsang Manual Control')
clock = pygame.time.Clock()

# Set up the camera
cam = picamera.camera.PiCamera()
cam.vflip = True
cam.hflip = True

# Print the interface info on the oled.
Lobsang.begin(splashscreen=False)
Lobsang.oled.clear_buffer()
Lobsang.oled.write("Manual Ctrl", pos=(0, 0), size=16)
Lobsang.oled.write("Control with W, A, S, D, ESC keys and mouse.")
Lobsang.oled.write("Left click to toggle laser, right to take picture.")
Lobsang.oled.refresh()

# Calibrate the motor speeds to run in an approximately straight line.
Lobsang.wheels.calibrate_speeds(-0.8)

old_time = time.time()
total_loops = 0

def over_difference(amount, val1, val2):
	# Checks difference between two values. If it's more than $amount, return False.
	if val1 - val2 > amount or val2 - val1 > amount:
		return False
	#if val1 - val2 < -amount or val2 - val1 < amount:
	#	return False
	return True

pygame.mouse.set_pos(250, 250) # Centre the mouse

try: # Put the main loop in a try statement to catch errors and stop the robot before exiting scipt.
	start_time = time.time()
	while True: # Loop indefinitely
		for event in pygame.event.get(): # Search through events for keys we need to respond to
			if event.type == KEYDOWN:
				if event.key == K_w:
					forward = True
				elif event.key == K_a:
					left = True
				elif event.key == K_s:
					backward = True
				elif event.key == K_d:
					right = True
				#elif event.key == K_t:
				#	text_to_say = ""
				#	while letter != K_ESCAPE and letter != K_RETURN:
				#		
			if event.type == KEYUP:
				if event.key == K_w:
					forward = False
				elif event.key == K_a:
					left = False
				elif event.key == K_s:
					backward = False
				elif event.key == K_d:
					right = False
			mouse_button_status = pygame.mouse.get_pressed()
			if mouse_button_status[0]:
				laser_state = not laser_state
				Lobsang.head.laser(laser_state)
			elif mouse_button_status[2]:
				cam.capture("images/%s.png" %str("Image_"+("_".join(time.asctime().split(" ")))))
				cam.capture("current.png", resize=(128, 64))
				Lobsang.oled.clear_buffer()
				Lobsang.oled.render("current.png")
				Lobsang.oled.refresh()
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # Exit program (ESC pressed or X button if in GUI).
				current_time = time.time()
				Lobsang.wheels.both(0, ramped=False)
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting Manual mode.") 
				print "Manual Control: main loop ran for %s seconds or %i times, with average time per loop of %fs and %s loops per second." %(str(int((current_time - start_time) * 100.0) / 100.0), total_loops, (current_time - start_time) / total_loops, str(int(1 / ((current_time - start_time) / total_loops) * 100.0) / 100.0))
				print "Manual Control: Halting."
				clock.tick(2)
				pygame.quit()
				Lobsang.oled.clear()
				sys.exit()
		pos = pygame.mouse.get_pos()
		if pos != old_pos:#True:#over_difference(3, pos[0], old_pos[0]):
			headX = 2000 - pos[0] * 2
			headY = pos[1] * 2 + 1000
			old_pos = pos
			Lobsang.head.aim(headX, headY)
		left_motor_speed = 0
		right_motor_speed = 0
		if forward and not True in (left, right, backward): # Only forward key pressed
			left_motor_speed = 16
			right_motor_speed = 16
			calibration = -0.15
		elif backward and not True in (forward, left, right): # Only backward key pressed
			left_motor_speed = -16
			right_motor_speed = -16
			calibration = -0.15
		elif left and not True in (forward, right, backward): # Only left key pressed
			left_motor_speed = -9
			right_motor_speed = 9
		elif right and not True in (forward, left, backward): # Only right key pressed
			left_motor_speed = 9
			right_motor_speed = -9
		elif forward and left and not right: # Both forward and left keys pressed, but not right. 
			left_motor_speed = 4
			right_motor_speed = 16
		elif forward and right and not left: # Both forward and right keys pressed, but not left.
			left_motor_speed = 16
			right_motor_speed = 4
		elif backward and left and not right: # Both backward and left keys pressed, but not right.
			left_motor_speed = -16
			right_motor_speed = -4
		elif backward and right and not left: # Both backward and right keys pressed, but not left.
			left_motor_speed = -4
			right_motor_speed = -16
		
		Lobsang.wheels.both(left_motor_speed, right_motor_speed)
		
		total_loops += 1
		clock.tick(loops_per_second)

except Exception as e:
	Lobsang.wheels.both(0, ramped=False)
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("Halting Manual Control.")
	print "An error occurred in Manual Control: %s. Halting." %e
	print "Manual Control: loop ran for %i seconds or %i times, with average time per loop = %fs" %(int(time.time() - start_time), total_loops, (time.time() - start_time) / total_loops)
	pygame.quit()
	time.sleep(0.5)
	Lobsang.quit(screensaver=False)
	# Exit

