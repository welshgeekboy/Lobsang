#!/usr/bin/env python
#
# three_point_turn.py-  a dead reckoning  attempt
# at the three point turn for PiWars. Very simple
# idea, very difficult to perfect! Describes a T-
# shape with the robot and attempts to  get  back
# to where the robot began, facing the other way.
#
# Created Dec 2015 by Finley Watson.

print "Three Point Turn: Initialising."

# Import the libraries we need.
import Lobsang
import time
#import pygame
#import sys
#from pygame.locals import *

Lobsang.oled.write("Starting Three Point Turn.")
Lobsang.oled.refresh()

# The sequence of directions, times and with motor calibration for each motor speed.
#                          FWD    LFT    FWD    BKD    FWD    LFT    FWD    STP  
wheels_direction_left  = (  16,    -8,    16,   -16,    16,    -8,    16,     0)
wheels_direction_right = (  16,     8,    16,   -16,    16,     8,    16,     0)
wheels_movement_time   = ( 4.7,  0.95,   1.3,   2.6,   1.2,  0.95,   4.7,   0.1)
wheels_calibration     = (-0.55, -0.4, -0.55, -0.55, -0.55,  -0.4, -0.55,   0.0)

# Set up Lobsang.
Lobsang.begin(splashscreen=False)
Lobsang.head.laser(True)
Lobsang.head.aim(1380, 1580)
time.sleep(4)

# Set up pygame here?
# pygame...

Lobsang.oled.clear_buffer()
Lobsang.oled.write("3PT", size=16)
Lobsang.oled.write("Running three point turn code...")
Lobsang.oled.write("No manual control!")
Lobsang.oled.refresh()

try:
	for i in range(len(wheels_movement_time)):
		Lobsang.wheels.calibrate_speeds(wheels_calibration[i])
		Lobsang.wheels.both(wheels_direction_left[i], wheels_direction_right[i])
		time.sleep(wheels_movement_time[i])
except:
	Lobsang.wheels.both(0)
	print "Three Point Turn: Exception occurred."
finally:
	print "Three Point Turn: Halting."
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("Halting Three Point Turn.")
	Lobsang.oled.refresh()
	time.sleep(0.5)
	Lobsang.quit(screensaver=False)

