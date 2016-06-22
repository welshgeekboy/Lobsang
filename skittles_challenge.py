#!/usr/bin/env python
#
# skittles_challenge.py-  allows the user to control
# Lobsang with the "W A S D" keys for  direction and
# "K O P" to control the ball  launching  appendage.
# O and P open and  close the ball guide and K opens
# the ball guide then releases the  launching paddle
# to fire the skittles ball at the pins. Uses pygame
# to get key presses,  and allows keys to be pressed
# at the  same time for  greater control so  you can
# drive left, left and forward,  only forward, right
# and forward etc. Press ESC to quit.
#
# Created Nov 2015 by Finley Watson.

print "Skittles Challenge: Initialising."

# Import all the libraries we need.
import Lobsang
import pygame
import sys
import time
from pygame.locals import *

# Give feedback on the oled.
Lobsang.oled.write("Starting Skittles Challenge.")
Lobsang.oled.refresh()

# All the variables needed.
loops_per_second = 50
left_motor_speed = 0
right_motor_speed = 0

forward = False
backward = False
left = False
right = False

launch_ball = False
paddle_open = False

open_guide = True
opened = True
redraw = False

# Set up pygame.
pygame.init()
DISPLAYSURF = pygame.display.set_mode((1280, 800))
pygame.display.set_caption('Lobsang Skittles Challenge')
clock = pygame.time.Clock()

# Set up Lobsang.
Lobsang.begin(splashscreen=False)
Lobsang.wheels.calibrate_speeds(-0.6)
Lobsang.head.aim(1380, 1550)
#Lobsang.head.laser(True)
# Tell the Duino that the launcher is connected.
Lobsang.launcher.connect()
Lobsang.launcher.open_guide()
Lobsang.launcher.reset_paddle()

# Print the interface info on the oled.
Lobsang.oled.clear_buffer()
Lobsang.oled.write("Skittles", pos=(0, 0), size=16)
Lobsang.oled.write("Control with W, A, S, D keys.")
Lobsang.oled.write("Control paddle with K, O, P keys.")
Lobsang.oled.write("Press ESC to quit.")
Lobsang.oled.refresh()

old_time = time.time()
total_loops = 0

try: # Put the main loop in a try statement to catch errors and stop the robot before exiting script.
	start_time = time.time()
	while True: # Loop indefinitely.
		for event in pygame.event.get(): # Search through events for keys we need to respond to.
			if event.type == KEYDOWN:
				rec = Lobsang.serial.read()
				if rec != '':
					print rec
				if event.key == K_w:
					forward = True
				elif event.key == K_a:
					left = True
				elif event.key == K_s:
					backward = True
				elif event.key == K_d:
					right = True
				elif event.key == K_k:
					launch_ball = True
				elif event.key == K_i:
					launch_ball = False
				elif event.key == K_o:
					open_guide = True
				elif event.key == K_p:
					open_guide = False
				
				if redraw: # Redraw default screen after a key is pressed after launching the ball.
					Lobsang.oled.clear_buffer()
					Lobsang.oled.write("Skittles", pos=(0, 0), size=16)
					Lobsang.oled.write("Control with W, A, S, D keys.")
					Lobsang.oled.write("Control paddle with K, I, O, P keys.")
					Lobsang.oled.write("Press ESC to quit.")
					Lobsang.oled.refresh(blackout=False)
					redraw = False
			
			if event.type == KEYUP:
				if event.key == K_w:
					forward = False
				elif event.key == K_a:
					left = False
				elif event.key == K_s:
					backward = False
				elif event.key == K_d:
					right = False
			
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				current_time = time.time()
				Lobsang.wheels.both(0, ramped=False)
				Lobsang.launcher.disconnect()
				Lobsang.head.laser(False)
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting Skittles Challenge code.") 
				Lobsang.oled.refresh(blackout=False)
				print "Skittles Challenge: Main loop ran for %s seconds or %i times, with average time per loop of %fs and %s loops per second." %(str(int((current_time - start_time) * 100.0) / 100.0), total_loops, (current_time - start_time) / total_loops, str(int(1 / ((current_time - start_time) / total_loops) * 100.0) / 100.0))
				print "Skittles Challenge: Halting."
				time.sleep(0.5)
				pygame.quit()
				Lobsang.quit(screensaver=False)
				sys.exit()
		
		left_motor_speed = 0
		right_motor_speed = 0
		if forward and not True in (left, right, backward): # Only forward key pressed
			left_motor_speed = 16
			right_motor_speed = 16
			#calibration = -0.6
		
		elif backward and not True in (forward, left, right): # Only backward key pressed
			left_motor_speed = -16
			right_motor_speed = -16
		
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
		
		else:
			left_motor_speed = 0
			right_motor_speed = 0
		
		if launch_ball and not paddle_open: # Launch ball from ball launcher and deal with guide all in one go.
			Lobsang.oled.clear_buffer()
			Lobsang.oled.write("Skittles", size=16)
			Lobsang.oled.write("Launching ball.")
			Lobsang.oled.refresh(blackout=False)
			Lobsang.launcher.launch_ball()
			Lobsang.oled.write("Launched ball. Did I score!?")
			Lobsang.oled.refresh(blackout=False)
			#Lobsang.launcher.reset_paddle()
			paddle_open = True
			redraw = True
		
		elif not launch_ball and paddle_open: # Paddle was manually closed. Reset the appendage to launch again.
			Lobsang.launcher.reset_paddle()
			paddle_open = False
		
		elif open_guide and not opened: # Open guide
			Lobsang.oled.clear_buffer()
			Lobsang.oled.write("Skittles", size=16)
			Lobsang.oled.write("Opened ball guide arm.")
			Lobsang.oled.refresh(blackout=False)
			Lobsang.launcher.open_guide()
			redraw = True
			opened = True
		
		elif not open_guide and opened: # Close guide
			Lobsang.oled.clear_buffer()
			Lobsang.oled.write("Skittles", size=16)
			Lobsang.oled.write("Closed ball guide arm.")
			Lobsang.oled.refresh(blackout=False)
			Lobsang.launcher.close_guide()
			opened = False
			redraw = True
		
		Lobsang.wheels.both(left_motor_speed, right_motor_speed)
		total_loops += 1
		clock.tick(loops_per_second)

except Exception as e:
	Lobsang.wheels.both(0, ramped=False)
	Lobsang.launcher.disconnect()
	Lobsang.head.laser(False)
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("Halting Skittles Challenge.")
	Lobsang.oled.refresh()
	print "An error occurred in Skittles Challenge: %s. Halting." %e
	print "Skittles Challenge: loop ran for %i seconds or %i times, with average time per loop = %fs" %(int(time.time() - start_time), total_loops, (time.time() - start_time) / total_loops)
	time.sleep(0.5)
	pygame.quit()
	Lobsang.quit(screensaver=False)
	# Exit
