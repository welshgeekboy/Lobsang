#!/usr/bin/env python
#
# Padlock.py-  a script that can allow or deny access
# to Lobsang.  Works  like a  login but you can use a 
# USB stick as a 'key' as  well as a passkey. The USB
# stick  must  have the same ID etc as  $correct_key,
# so there is only one stick that will work. Designed
# to be used as a library.  attempt_unlock()  returns
# True if the user entered the correct USB  stick  or
# manually  entered passkey,  and  False if the login
# failed.
#
# Created Nov 2015 by Finley Watson (@welshgeekboy)

import os

# The three correct keys- USB stick ID or a 4-digit code, manually entered.
correct_keys = ["ID 1781:557d SanDisk Corp. Cruzer"]
correct_passkey = "4198"

unlocked = True
VERBOSE = False

def attempt_unlock():
	_unlocked = False
	tries = 5
	if VERBOSE:
		print "Lock: Running."
		print "Lock: Searching USB bus for devices..."
	
	os.system("lsusb > usbs.txt")
	with open("usbs.txt", "r") as usblist:
		keys = usblist.readlines()
	os.system("rm usbs.txt")
	
	for correct_key in correct_keys:
		for key in keys:
			if correct_key in key:
				_unlocked = True
				if VERBOSE: print "Lock: Correct USB device found. You have gained system access."
				return True
	
	if VERBOSE: print "Lock: USB key not found. Will attempt passkey entry instead."
	while not _unlocked and tries > 0:
		try:
			passkey = raw_input("Enter passkey (%i): " %tries)
			if passkey == correct_passkey:
				_unlocked = True
				if VERBOSE: print "Lock: Entered correct passkey. You have gained system access."
				return True
			if VERBOSE: print "Lock: Entered incorrect passkey."
			if tries <= 0:
				if VERBOSE: print "Lock: Entered incorrect passkey. You have failed to gain system access."
				break
			else:
				tries -= 1
		except:
			print
			tries -= 1
	return False


if __name__ == "__main__":
	VERBOSE = True
	attempt_unlock()
