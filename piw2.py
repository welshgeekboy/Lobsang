#!/usr/bin/env python

# piwars_menu.py - A way of calling the different
# scripts for each challenge without looking at a
# standard screen.  Displays info on the oled and
# runs Pi Wars scripts which (on exit) allow this
# script to keep running.  Use the number keys to
# select the script you want to run,  UP and DOWN
# to scroll the menu or ESC to exit program.
#
# Created Nov 2015 by Finley Watson

print "Piwars Menu: Initialising."

import Lobsang
import time
import sys
import pygame
from pygame.locals import *
import os

Lobsang.oled.write("Starting Piwars Menu.")
# Check if we have access to GPIO ports- was script run with 'sudo'?
if not Lobsang.gpio_access:
	Lobsang.oled.write("No GPIO access!")
	Lobsang.oled.refresh()
	time.sleep(0.5)	
	Lobsang.oled.clear()
	sys.exit() # Exit program.

Lobsang.oled.refresh()

fps = 10 # Number of loop cycles per second.
menu_position = 0 # Oled menu position (0 - 3)
# All the options that are supported by this script. The spaces make the text appear right-alined (purely aesthetic!).
menu_options = ["1:                            Line follower",
		"2:                       Manual control",
		"3:               Drag race control",
		"4:                          Proximity test",
		"5:                Skittles challenge",
		"6:                   Three point turn",
		"7:                      Backup all files",
		"8:              Shutdown Lobsang",
		"ESC:              Exit Piwars Menu"]

# Set up pygame for a HDMIPi screen so 1280 x 800 px, but size does not matter.
pygame.init()
display = pygame.display.set_mode((1280, 800))
pygame.display.set_caption('Piwars Program Select Menu') # This only shows if you are using the GUI, not the terminal.
clock = pygame.time.Clock()

def render_menu(menu_pos):
	'''Displays the menu on the OLED at the position
	   set by up/down keys. Not all of the menu
	   is visible at any one time. This scrolls it.'''
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("  PiWars Menu", size=16) # Write the title at the top.
	for i in range(menu_pos, menu_pos + 4): # From top to bottom of the *scrolled* menu (not all of the menu), write each option that is visible.
		Lobsang.oled.write(menu_options[i], size=8)
	Lobsang.oled.refresh(blackout=False) # Refresh the screen to display the new data but don't blank the screen while it's being updated- this makes transition much smoother.

render_menu(0) # Display the menu at the automatic starting point- at the top.
while True: # Loop indefinitely, waiting to run the piwars programs.
	for event in pygame.event.get():
		if event.type == KEYDOWN: # Check for keys pressed down
			if event.key == K_1:
				# Key '1' pressed. Run the line follow program 'line_follower.py'.
				print "Piwars Menu: Running line follow program..."
				pygame.quit() # Halt the pygame window to stop a weird freeze when more than one pygame window opens in the terminal, and so you can see any terminal messages printed by script run below.
				os.system("sudo python line_follower.py")
				print "Piwars Menu: Finished running line follow program. Continuing running menu."
				render_menu(menu_position)
				pygame.init() # After the script has finished, restart the pygame window to continue getting keyboard events.
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_2:
				# Key '2' pressed. Run the manual control program 'manual_control.py'.
				print "Piwars Menu: Running manual control program..."
				pygame.quit()
				os.system("sudo python manual_control.py")
				print "Piwars Menu: Finished running manual control program. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_3:
				# Key '3' pressed. Run the drag race style manual control program 'drag_race.py'.
				print "Piwars Menu: Running straight line speed test program..."
				pygame.quit()
				os.system("sudo python drag_race.py")
				print "Piwars Menu: Finished running straight line speed test program. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_4:
				# Key '4' pressed. Run the proximity alert program 'proximity_alert.py'.
				print "Piwars Menu: Running proximity alert program..."
				pygame.quit()
				os.system("sudo python proximity_alert.py")
				print "Piwars Menu: Finished running proximity alert program. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_5:
				# Key '5' pressed. Run the manual control skittles / bowling program 'skittles_challenge.py'
				print "Piwars Menu: Running skittles challenge program..."
				pygame.quit()
				os.system("sudo python skittles_challenge.py")
				print "Piwars Menu: Finished running skittles program. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_6:
				print "Piwars Menu: Running three point turn program..."
				pygame.quit()
				os.system("sudo python three_point_turn.py")
				print "Piwars Menu: Finished running three point turn program. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_7:
				# Key '7' pressed. Back up files in ~/lobsang/ and ~/sketchbook to a USB stick using program 'backup.sh'.
				print "Piwars Menu: Will now back up files..."
				pygame.quit()
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Backup", size=16)
				Lobsang.oled.write("Please insert USB stick.")
				Lobsang.oled.refresh()
				os.system("sudo bash bash/backup.sh")
				Lobsang.oled.write("Copied data.")
				Lobsang.oled.refresh()
				time.sleep(2)
				print "Piwars Menu: Finished backing up files. Continuing running menu."
				render_menu(menu_position)
				pygame.init()
				display = pygame.display.set_mode((1280, 800))
			
			elif event.key == K_8:
				# Key '8' pressed. Shuts down the robot by running 'sudo halt' then waiting for 10 secs
				# (before this time is up the program gets stopped as the system shuts down. The delay
				# is so that this program does not exit back to 'autorun.py' as that prompts a login as the Pi shuts down!).
				print "Piwars Menu: Will now shut down robot. Halting menu."
				pygame.quit()
				Lobsang.halt()
				time.sleep(10)
				
			elif event.key == K_UP:
			# Up key pressed. Scroll the menu options up one line.
				if menu_position > 0:
					menu_position -= 1
					render_menu(menu_position)
			
			elif event.key == K_DOWN:
			# Down key pressed. Scroll the menu options down one line.
				if menu_position < len(menu_options) - 4: # Use len() to make the menu adaptable. Add and remove menu items and this will still scroll right.
					menu_position += 1
					render_menu(menu_position)
			
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			# ESC (or close button if in X windows) pressed. Exit this program, 'piwars_menu.py'.
				print "Piwars Menu: Halting."
				Lobsang.duino.disable()
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting Piwars Menu.")
				Lobsang.oled.refresh()
				pygame.quit()
				Lobsang.oled.clear()
				sys.exit()
	clock.tick(fps)
