#!/usr/bin/env python
#
# line_follower.py- Sixth attempt at line following.
# There is still a slight  oscillation over the line
# but it is not a major problem-   fastest speeds so
# far are 0.208m/s on a smooth but sharpish cornered
# track.  Lobsang's top speed is 0.286m/s so this is
# not far off normal straight  operation  top speed.
#
# Created Nov 2015 by Finley Watson.

print "Line Follower: Initialising."

# Import all the libraries we need.
import Lobsang
import time
import os
from sys import exit
import pygame
from pygame.locals import *

# Give feedback on the oled.
Lobsang.oled.write("Starting Line Follower.")
Lobsang.oled.refresh()
Lobsang.begin(splashscreen=False)
Lobsang.wheels.calibrate_speeds(-0.6)

DEBUG = True
SHOW_MAP = False

if DEBUG: print "Line Follower: Debug is on. Will print program info."
if SHOW_MAP: print "Line Follower: Map is on. Will print line map each loop."

black    = 1
white    = 0
map      = [white, white, white]
old_map  = [white, white, white]
left     = [black, white, white]
left_90  = [black, black, white]
middle   = [white, black, white]
right    = [white, white, black]
right_90 = [white, black, black]
blank    = [white, white, white]

loops_per_second = 51
allowed_to_run = False

total_loops = 0

direction = "stop"
old_direction = "stop"

# Set up pygame so we can get key presses.
pygame.init()
display = pygame.display.set_mode((1280, 800))
pygame.display.set_caption("Line Follower Program")
clock = pygame.time.Clock()

left_two = [-4, 15]
left_one = [6, 13]
fwd      = 10
rght_one = [13, 6]
rght_two = [15, -4]
  
old_time = time.time()
current_time = time.time()

# Show interface info on the oled.
Lobsang.oled.clear_buffer()
Lobsang.oled.write("Line Follow", size=16)
Lobsang.oled.write("Press SPACE to start.")
Lobsang.oled.write("Press ESC to quit.")
Lobsang.oled.refresh()
Lobsang.head.aim(1430, 1800)

print "Line Follower: Running main loop."
if DEBUG: os.system("printf 'Motors: stop for '") # The robot begins stationary, so print that if $DEBUG.

try: # Put the main loop in a try statement to stop the robot and exit cleanly on an Exception.
	start_time = time.time() # The time the loop began- used in calculating info at exit (See print statements below).
	while True:
		clock.tick(loops_per_second) # You don't need the robot testing as fast as it can.
		total_loops += 1
		map = Lobsang.sensors.line_map() # Read the IR line follow sensor connected to the Pi's GPIO.
		if SHOW_MAP: print "Line map:", map; print "Line buffer:", line_buffer; print # If $SHOW_MAP, display the array of 3 0s or 1s (sensor readings).
		
		# Search through all events for key presses we have to deal with.
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_SPACE: # Toggle running the line follow code.
					allowed_to_run = not allowed_to_run
					if allowed_to_run:
						Lobsang.oled.clear_buffer()
						Lobsang.oled.write("Line Follow", size=16)
						Lobsang.oled.write("Press SPACE to stop.")
						Lobsang.oled.write("Press ESC to quit.")
						Lobsang.oled.refresh(blackout=False)
						Lobsang.duino.enable()
						# Continue in the last direction of travel or the robot gets confused. 
						if direction == "forward":
							Lobsang.wheels.both(fwd)
						elif direction == "left":
							Lobsang.wheels.both(left_one[0], left_one[1])
						elif direction == "right":
							Lobsang.wheels.both(rght_one[0], rght_one[1])
					else:
						Lobsang.duino.disable()
						Lobsang.oled.clear_buffer()
						Lobsang.oled.write("Line Follow", size=16)
						Lobsang.oled.write("Press SPACE to start.")
						Lobsang.oled.write("Press ESC to quit.")
						Lobsang.oled.refresh(blackout=False)
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # Exit program
				current_time = time.time()
				Lobsang.duino.disable()
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting Line Follower.")
				Lobsang.oled.refresh()
				pygame.quit()
				if DEBUG: print " " # Add a carriage-return.
				print "Line Follower: Halting"
				print "Line Follower: main loop ran for %s seconds or %i times, with average time per loop of %fs and %s loops per second." %(str(int((current_time - start_time) * 100.0) / 100.0), total_loops, (current_time - start_time) / total_loops, str(int(1 / ((current_time - start_time) / total_loops) * 100.0) / 100.0))
				time.sleep(0.5)
				Lobsang.quit(screensaver=False)
				exit()
		if allowed_to_run: # Only follow the line if the SPACE key has been pressed.
			if map != old_map: # Avoid code repeats when the line is still under the same place on the sensor.
				old_map = map
				
				if map == middle: # Line is under centre sensor- go forward.
					direction = "forward"
					Lobsang.wheels.both(fwd)
				
				elif map == left or map == left_90: # Line is under the left sensor (and possibly under middle sensor too)- turn left.
					direction = "left"
					Lobsang.wheels.both(left_one[0], left_one[1])
							
				elif map == right or map == right_90: # Line is under the right sensor (and possibly under middle sensor too)- turn right.
					direction = "right"
					Lobsang.wheels.both(rght_one[0], rght_one[1])
				
				elif map == blank: # Line is under none of the sensors- either between the sensors so they don't see it, or to the left or right of the sensor head.
					if direction == "left": # If the line is not under the sensor and the robot is turning left, make it turn left more sharply as it is understeering.
						direction = "extreme left"
						Lobsang.wheels.both(left_two[0], left_two[1])
					elif direction == "right": # If the line is not under the sensor and the robot is turning right, make it turn right more sharply as it is understeering.
						direction = "extreme right"
						Lobsang.wheels.both(rght_two[0], rght_two[1])
				
				if DEBUG and direction != old_direction: # If $DEBUG and the direction of the motors have changed, print the time spent in the previous direction, a carriage return, and the current direction.
					os.system("printf '%fs\r\nMotors: %s for '" %(((time.time() - old_time) * 10000) / 10000.0, direction))
					old_direction = direction
					old_time = time.time()

except Exception as e:
	Lobsang.duino.disable()
	if DEBUG: print "" # Add a carriage-return.
	print "Line Follower: main loop ran for %s seconds or %i times, with average time per loop of %fs and %s loops per second." %(str(int((current_time - start_time) * 100.0) / 100.0), total_loops, (current_time - start_time) / total_loops, str(int(1 / ((current_time - start_time) / total_loops) * 100.0) / 100.0))
	print "An error occurred in Line Follower: %s. Halting." %e
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("Error in line follow code. Halting.", pos=(0, 24))
	Lobsang.oled.refresh()
	time.sleep(2)
	Lobsang.quit(screensaver=False)
	# Exit
