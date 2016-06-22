#!/usr/bin/env python
#
# drag_race.py- works like manual control script
# except  left and  right  controls are  greatly
# reduced so the robot mostly goes in a straight
# line.  This is designed for the straight  line
# speed test so the robot does not need to turn.
#
# Created Dec 2015 by Finley Watson

print "Straight Line Speed Test: Initialising."

# Import all the libraries we need.
import Lobsang
import pygame
import sys
import time
from pygame.locals import *

# Give feedback to the oled.
Lobsang.oled.write("Starting Straight Line Speed Test code (manual control)")
Lobsang.oled.refresh()

# All the variables we need.
loops_per_second = 100
total_loops = 0

left_motor_speed = 0
right_motor_speed = 0

forward = False
backward = False
left = False
right = False

# Set up pygame.
pygame.init()
DISPLAYSURF = pygame.display.set_mode((1280, 800))
pygame.display.set_caption('Lobsang Manual Control')
clock = pygame.time.Clock()

# Set up Lobsang and switch on the laser guidance system (a laser pointing forwards!).
Lobsang.begin(splashscreen=False)
Lobsang.wheels.calibrate_speeds(-0.7)
Lobsang.head.aim(1380, 1700)
Lobsang.head.laser(True)

# Display the default info on the oled.
Lobsang.oled.clear_buffer()
Lobsang.oled.write("Manual Ctrl", size=16)
Lobsang.oled.write("Straight Line Speed Test mode.")
Lobsang.oled.write("Awaiting instructions...")
Lobsang.oled.refresh()

try: # So except: can stop the robot before script exits.
	start_time = time.time() # The time the main code started running.
	while True: # Loop indefinitely.
		for event in pygame.event.get(): # Search through events for keys we need to respond to. 
			if event.type == KEYDOWN:
				if event.key == K_w:
					forward = True
				elif event.key == K_a:
					left = True
				elif event.key == K_s:
					backward = True
				elif event.key == K_d:
					right = True
			
			if event.type == KEYUP:
				if event.key == K_w:
					forward = False
				elif event.key == K_a:
					left = False
				elif event.key == K_s:
					backward = False
				elif event.key == K_d:
					right = False
				elif event.key == K_SPACE:
					stop = False
			
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # Exit program (ESC pressed or X button if in GUI).
				Lobsang.wheels.both(0, ramped=False)
				Lobsang.head.laser(False)
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting Straight Line Speed Test.")
				Lobsang.oled.refresh()
				print "Straight Line Speed Test: main loop ran for %s seconds or %i times, with average time per loop of %fs and %s loops per second." %(str(int((current_time - start_time) * 100.0) / 100.0), total_loops, (current_time - start_time) / total_loops, str(int(1 / ((current_time - start_time) / total_loops) * 100.0) / 100.0))
				clock.tick(2)
				pygame.quit()
				Lobsang.quit(screensaver=False)
				sys.exit()
		left_motor_speed = 0
		right_motor_speed = 0
		if forward and not left and not right:
			left_motor_speed = 16
			right_motor_speed = 16
		
		elif forward and left:
			left_motor_speed = 14
			right_motor_speed = 16
		
		elif forward and right:
			left_motor_speed = 16
			right_motor_speed = 14
		
		elif backward and not left and not right:
			left_motor_speed = -10
			right_motor_speed = -10
		
		elif backward and left:
			left_motor_speed = -10
			right_motor_speed = -9
		
		elif backward and right:
			left_motor_speed = -9
			right_motor_speed = -10
		
		elif left and not right and not forward and not backward:
			left_motor_speed = -6
			right_motor_speed = 6
		
		elif right and not left and not forward and not backward:
			left_motor_speed = 6
			right_motor_speed = -6
		
		Lobsang.wheels.both(left_motor_speed, right_motor_speed)
	
		total_loops += 1
		clock.tick(loops_per_second)
		
except Exception as e:
	Lobsang.wheels.both(0)
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("Halting Straight Line Speed Test.")
	Lobsang.oled.refresh()
	print "Straight Line Speed Test: An error occurred: '%s'" %e
	print "Straight Line Speed Test: Loop ran for %s seconds or %i times, with average time per loop = %fs" %(str(int((time.time() - start_time) * 10) / 10.0), total_loops, (time.time() - start_time) / total_loops)
	time.sleep(0.5)
	pygame.quit()
	Lobsang.quit(screensaver=False)
