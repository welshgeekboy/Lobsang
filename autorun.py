#!/usr/bin/env python
#
# autorun.py- checks if robot systems are all online
# and if they are then it will run the main  program
# (currently piwars_menu.py)  but if  Lobsang cannot
# run due to eg the Duino being unplugged, then this
# will give a login prompt. A numeral passkey or USB
# 'key' (correct usb stick)  is required  to  access
# the terminal, like a standard linux login.
#
# To disable automatic running of this file once per
# boot on tty1 at boot completion edit /etc/rc.local
# and comment out the  correct line near the bottom.
#
# Created Jun 2016 by Finley Watson

print "Auto Run: Initialising."

# Import the necessary libraries
import Oled
import Padlock
import random
import time
import subprocess
import os
import sys

# Display a message on the oled, if it works.
try: # We have not yet checked if the OLED is connected, so only "try:" to do this.
	Oled.write("Starting Auto Run.")
	Oled.refresh()
except: # Oled failed, but don't cause a fuss.
	pass

# Variables to be set lower down
camera_online = True
oled_online = True
duino_online = True

# Run boot.py, a system checkup script.
boot_errors = subprocess.call(["python", "boot.py"])

# Script exit code gives info about systems: 0 is all online,
# +4 == camera offline, +2 == oled offline, +1 == duino offline.
# So an error code of 6 == oled and cam offline but error of
# 5 == camera and duino offline. This data is split into each part below.
# If no GPIO access then boot.py always exits with code 16.

if boot_errors > 0: # There ARE errors to be handled.
	boot_errors_original = boot_errors
	if boot_errors == 16: # 'No GPIO access' code.
		print "Auto Run: No GPIO access."
		sys.exit()
	if boot_errors >= 4: # >= 4 == 'camera offline'.
		boot_errors -= 4 # Remove 'camera offline' code.
		camera_online = False
	if boot_errors >= 2: # >= 2 == 'oled_offline'.
		boot_errors -= 2 # Remove 'oled offline' code.
		oled_online = False
	if boot_errors >= 1: # >= 1 == 'duino offline' code.
		boot_errors -= 1 # Now $boot_errors should == 0
		duino_online = False
	if boot_errors != 0: # This should never happen!
		print "Auto Run: Error checking for boot errors. Wrong error code returned from boot.py? Error code == %i" %boot_errors_original
if duino_online:
	if oled_online:
		Oled.clear_buffer()
		Oled.write("Auto Run: %i/4 systems online." %(camera_online + oled_online + duino_online + 1)) # Display the number of systems online (+ 1 because Pi is online - the fourth system)
		Oled.refresh()
		Oled.command(Oled.on)
	print "Auto Run: Success! System is stable."
	os.system("sudo python menu.py")

else: # Duino is offline.
	print "Auto Run: Cannot boot Lobsang!"
	if oled_online:
		Oled.write("Auto Run: Cannot boot Lobsang!")
		Oled.refresh()

# Runs after piwars_menu.py exits or on 'system not stable' error.
print "Auto Run: Please login with passkey or USB stick."
if oled_online:
	Oled.clear_buffer()
	Oled.write("Please login with passkey or USB stick")
	Oled.refresh()

# This returns a boolean value, which tells the code if the login was successful.
attempt = Padlock.attempt_unlock()

if attempt == Padlock.unlocked:
	if oled_online:
		Oled.write("Login successful")
		Oled.refresh(blackout=False)
	print "Auto Run: System access gained."
	if oled_online:
		time.sleep(1)
		Oled.clear()
	print "Auto Run: Exit program."
else:
	if oled_online:
		Oled.write("Login failed!")
		Oled.refresh(blackout=False)
	print "Auto Run: Login failed. Sleeping forever..."
	# ! WARNING !
	# This cannot be halted!!! Pi reboot needed to exit loop.
	# ^Z does not send it to background as keyboard interrupts
	# do not work at the point when this file is run- only 
	# AFTER user is first given bash console prompt. This runs
	# just before. If you run this in the terminal then ^Z can
	# send it to the background, but not terminate it.
	while True: # Just keep sleeping forever!
		try:
			time.sleep(10000) # <--- The teenage dream
		except: # An error? Ah well, carry on sleeping! *Infuriates hacker* :-D
			pass
