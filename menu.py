#!/usr/bin/env python
#
# menu.py - A way of calling the different scripts on
# Lobsang  without  looking  at  a  standard  screen.
# Displays  info on the oled, and runs scripts.  When
# the script ends, this menu continues  running. This
# allows you to run  multiple demos etc. very easily.
# Use the  enter key to run the  selected script that
# the cursor is beside, shown on the oled.  UP & DOWN
# keys  scroll the  menu and  cursor  and ESC  exits.
#
# Created Aug 2016 by Finley Watson

print "Menu: Initialising."

import Lobsang
import time
import sys
import pygame
from   pygame.locals import *
import os
import string

Lobsang.oled.write("Starting Menu.")
Lobsang.oled.refresh()

fps = 30 # Number of loop cycles per second.
menu_position = 0 # Menu options position.
cursor_position = 0 # Cursor position up / down only.
# All the options that are supported by this script. 2nd array part consists of commands that run the options.
standard_menu_options =	[["     Line follower",
			  "     Manual control",
			  "     Proximity alert",
			  "     Neural network 'dist'",
			  "     Load all programs",
			  "     Shut down Lobsang",
			  "     Exit Menu (ESC)"],
			 ["sudo python line_follower.py",
			  "sudo python manual_control.py",
			  "sudo python proximity_alert.py",
			  "sudo python nndist.py",
			  "LOAD_ALL_OPTIONS",
			  "SHUTDOWN",
			  "EXIT"]]

menu_options = standard_menu_options

ignored_files =("menu.py",
		"Lobsang.py",
		"Oled.py",
		"Padlock.py",
		".Padlock.py")

# The icon that is used to represent the cursor position.
cursor_icon =  [[1,1,0,0,0,0,0,0],
		[1,1,1,1,0,0,0,0],
		[1,1,1,1,1,1,0,0],
		[1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,1,1],
		[1,1,1,1,1,1,0,0],
		[1,1,1,1,0,0,0,0],
		[1,1,0,0,0,0,0,0]]

# Set up pygame and the pygame window for getting keypresses
# and displaying the OLED buffer on a standard screen too.
pygame.init()
window_size = (480, 240)
display = pygame.display.set_mode(window_size)
pygame.display.set_caption('Program Menu') # This shows if you are using X windows, but not in the terminal.
clock = pygame.time.Clock()

def render_menu(menu_pos, cursor_pos):
	'''Displays the menu on the OLED at the position
	   set by up/down keys. Not all of the menu
	   is visible at any one time. This scrolls it.'''
	Lobsang.oled.clear_buffer()
	Lobsang.oled.write("File Menu", size=16) # Write the title at the top.
	for i in range(menu_pos, menu_pos + 4): # From top to bottom of the *scrolled* menu (not all of the menu), write each option that is visible.
		Lobsang.oled.write(menu_options[0][i], size=8)
	Lobsang.oled.custom_icon(cursor_icon, pos=(0, cursor_pos * 9 + 22)) # Draw the cursor icon onto the right hand side of the screen.
	Lobsang.oled.refresh(blackout=False) # Refresh the screen to display the new data but don't blank the screen while it's being updated- this makes transition much smoother.
	Lobsang.oled.screenshot("current.png")
	display.blit(pygame.transform.scale(pygame.image.load("current.png"), window_size), (0, 0))
	pygame.display.update()

def all_programs_options():
	files_menu_options = [[] , []] 
	for file in os.listdir("/home/pi/lobsang/"):
		if file.endswith(".py") and not file in ignored_files:
			files_menu_options[0].append("     %s" %file[:len(file) - 3])
			files_menu_options[1].append("sudo python %s" %file)
	files_menu_options[0].append("     Back to standard menu")
	files_menu_options[1].append("LOAD_STANDARD_OPTIONS")
	files_menu_options[0].append("     Shutdown Lobsang")
	files_menu_options[1].append("SHUTDOWN")
	files_menu_options[0].append("     Exit menu (ESC)")
	files_menu_options[1].append("EXIT")
	return files_menu_options

render_menu(menu_position, cursor_position) # Display the menu.
while True: # Loop indefinitely, waiting to run programs or other commands.
	for event in pygame.event.get():
		if event.type == KEYDOWN: # Check for keys pressed down.
			if event.key == K_RETURN:
				# Return key pressed. Run the program or command under the cursor.
				option_name    = menu_options[0][menu_position + cursor_position][5:]
				option_command = menu_options[1][menu_position + cursor_position]
				
				# First check if the line under the cursor on the menu is an in-program command.
				if option_command == "LOAD_ALL_OPTIONS":
					menu_options = all_programs_options()
					menu_position = 0
					cursor_position = 0
					render_menu(menu_position, cursor_position)
				
				elif option_command == "LOAD_STANDARD_OPTIONS":
					menu_options = standard_menu_options
					menu_position = 0
					cursor_position = 0
					render_menu(menu_position, cursor_position)
				
				elif option_command == "SHUTDOWN":
					print "Menu: Shutting down Lobsang..."
					pygame.quit()
					Lobsang.halt()
					time.sleep(10)
									
				elif option_command == "EXIT":
					print "Menu: Halting menu."
					Lobsang.oled.clear_buffer()
					Lobsang.oled.write("Halting menu...")
					Lobsang.oled.refresh()
					pygame.quit()
					Lobsang.quit(False)
					sys.exit()
				else:
					# If the option's command is one for the terminal, run it as one.
					print "Menu: Running %s..." %string.lower(option_name)
					pygame.quit() # Halt the pygame window because only one pygame window can be open at once, and so you can see any terminal messages printed by script run below.
					os.system(option_command)
					print "Menu: Finished running %s. Continuing running menu." %string.lower(option_name)
					pygame.init() # After the script has finished, restart the pygame window to continue getting keyboard events.
					display = pygame.display.set_mode(window_size)
					render_menu(menu_position, cursor_position)
			
			elif event.key == K_UP:
				# Up key pressed. Scroll the menu options up one line, or the cursor up one line.
				if menu_position > 0 and cursor_position == 0:
					menu_position -= 1
					render_menu(menu_position, cursor_position)
				elif cursor_position > 0:
					cursor_position -= 1
					render_menu(menu_position, cursor_position)
				
			elif event.key == K_DOWN:
				# Down key pressed. Scroll the menu options down one line, or the cursor down one line.
				if menu_position < len(menu_options[0]) - 4 and cursor_position == 3: # Use len() to make the menu adaptable. Add and remove menu items and this will still scroll correctly.
					menu_position += 1
					render_menu(menu_position, cursor_position)
				elif cursor_position < 3:
					cursor_position += 1
					render_menu(menu_position, cursor_position)
			
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# ESC (or close button if in X) pressed. Exit this program, 'menu.py'.
				print "Menu: Halting menu."
				Lobsang.oled.clear_buffer()
				Lobsang.oled.write("Halting menu...")
				Lobsang.duino.disable()
				pygame.quit()
				Lobsang.quit(False)
				sys.exit()
	clock.tick(fps)
