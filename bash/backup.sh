#!/bin/bash
#
# backup(.sh)-  will mount,  copy  data
# to, then unmount my USB stick. As the
# Pi A+ has only one USB port,  copying
# data  is   somewhat  difficult.  This
# script starts a countdown to give you
# time to  swap the  wireless  keyboard
# dongle and the USB stick, then copies
# over all the important data and  code
# for adding to the git repository, and
# creates a complete  backup  including
# adding files that don't get copied to
# the GitHub folder.  Files  to  ignore
# are put in   /home/pi/lobsang/.ignore
# and do not get copied  to the  GitHub
# folder.
#
# Command-line  arguments  are:  -e  to
# open the file for  editing.  When you
# save  and  close  the  file,   it  is
# automatically  updated  in  /usr/bin/
# and /home/pi/lobsang/bash/
#
# [ TODO ] add the other args' info.
#
# Created May 2016 by Finley Watson.


# Possible command line arguments (all 0 or 1)
# When they have nothing after '=' sign they are false.
# list_usb_folder prints the contents of /media/DRIVE/Lobsang/github (auto off)
# delay toggles the 10s delay (auto on)
# unmount_when_finished will unmount the drive if 1 (auto on)
# verbose prints info as the copying occurs (auto on)
list_usb_folder=
delay=1
unmount_when_finished=1
verbose=1

# A crude way of checking for command line arguments.
if [ -n "$1" ] ; then
	if [ "$1" == "-u" ] || [ "$1" == "-update" ] ; then
		echo "Updating /usr/bin/backup to the latest backup file in /home/pi/lobsang/bash..."
		sudo cp /home/pi/lobsang/bash/backup.sh /usr/bin/backup
		exit 0
	elif [ "$1" == "-e" ] || [ "$1" == "--edit" ] ; then
		echo "Opening backup file for editing..."
		nano /home/pi/lobsang/bash/backup.sh
		sudo backup -u
		echo "Updated file."
		exit 0
	elif [ "$1" == "-l" ] || [ "$1" == "-list" ] ; then
		list_usb_folder=1
	elif [ "$1" == "-i" ] || [ "$1" == "-immediate" ] ; then
		delay=
	elif [ "$1" == "-m" ] || [ "$1" == "--leave-mounted" ] ; then
		unmount_when_finished=
	elif [ "$1" == "-q" ] || [ "$1" == "--quiet" ] ; then
		verbose=
	fi
	if [ -n "$2" ] ; then
		if [ "$2" == "-l" ] || [ "$2" == "-list" ] ; then
			list_usb_folder=1
		elif [ "$2" == "-i" ] || [ "$2" == "-immediate" ] ; then
			delay=
		elif [ "$2" == "-m" ] || [ "$2" == "--leave-mounted" ] ; then
			unmount_when_finished=
		elif [ "$2" == "-q" ] || [ "$2" == "--quiet" ] ; then
			verbose=
		fi
		if [ -n "$3" ] ; then
			if [ "$3" == "-l" ] || [ "$3" == "-list" ] ; then
				list_usb_folder=1
			elif [ "$3" == "-i" ] || [ "$3" == "-immediate" ] ; then
				delay=
			elif [ "$3" == "-m" ] || [ "$3" == "--leave-mounted" ] ; then
				unmount_when_finished=
			elif [ "$3" == "-q" ] || [ "$3" == "--quiet" ] ; then
				verbose=
			fi
			if [ -n "$4" ] ; then
				if [ "$4" == "-l" ] || [ "$4" == "-list" ] ; then
					list_usb_folder=1
				elif [ "$4" == "-i" ] || [ "$4" == "-immediate" ] ; then
					delay=
				elif [ "$4" == "-m" ] || [ "$4" == "--leave-mounted" ] ; then
					unmount_when_finished=
				elif [ "$4" == "-q" ] || [ "$4" == "--quiet" ] ; then
					verbose=
				fi
			fi
		fi
	fi
fi

if [ $verbose ] ; then
	echo    "Will now copy, including child directories, excluding files and folders in /home/pi/lobsang/.ignore:"
	echo -e "\t/home/pi/lobsang/*"
	echo -e "\t/home/pi/sketchbook/*"
	echo -e "\t/home/pi/.bashrc"
	echo
	echo "Please insert USB stick."
fi

# Waits for tens seconds before copying, with a visual countdown.
# Gives the user time to plug in the USB stick.
if [ $delay ] ; then
	if [ $verbose ] ; then
		for value in `seq 0 10` ; do
			printf "Time before copy begins: $((10-value))s \r"
			sleep 1
		done
		echo "USB stick should now be plugged in."
	else
		sleep 10
	fi
fi

if [ $verbose ] ; then
	echo "ls /dev/sd* gives:"
	ls /dev/sd*
	echo "It is important that there is only one device under /dev/sd* as this program picks the last device, alphabetically (eg. sde1 is picked over sda1)"
	echo "Copying..."
fi

sleep 1

# Clear the dump file of old data.
if [ $verbose ] ; then
	echo -e "\tClearing old data dump file /tmp/backup_dump."
fi
echo "File in which all error output from /bin/backup is dumped" > /tmp/backup_dump

# Mount the USB stick.
if [ $verbose ] ; then
	echo -e "\tMounting USB stick at /media/DRIVE"
fi

echo "Trying to mount usb stick..." >> /tmp/backup_dump
sudo mkdir /media/DRIVE 2>> /tmp/backup_dump
sudo mount /dev/sd*1 /media/DRIVE 2>> /tmp/backup_dump

# Just in case the directories don't exist (very unlikely)
# try to create them. Send stderr to a dump file in /tmp/
if [ $verbose ] ; then
	echo -e "\tAttempting to create directories if they don't exist already."
fi

echo "Trying to create directories that should already exist..." >> /tmp/backup_dump
sudo mkdir /media/DRIVE/Lobsang/                   2>> /tmp/backup_dump
sudo mkdir /media/DRIVE/Lobsang/github/            2>> /tmp/backup_dump
sudo mkdir /media/DRIVE/Lobsang/github/sketchbook/ 2>> /tmp/backup_dump
sudo mkdir /media/DRIVE/Lobsang/backup/            2>> /tmp/backup_dump
sudo mkdir /media/DRIVE/Lobsang/backup/sketchbook/ 2>> /tmp/backup_dump

# Copy over all the all files to be backed up.
if [ $verbose ] ; then
	echo -e "\tCopying over all files..."
fi
echo "Trying to copy over all files..." >> /tmp/backup_dump
cp -r /home/pi/lobsang/*    /media/DRIVE/Lobsang/github/            2>> /tmp/backup_dump
cp -r /home/pi/sketchbook/* /media/DRIVE/Lobsang/github/sketchbook/ 2>> /tmp/backup_dump
cp    /home/pi/.bashrc      /media/DRIVE/Lobsang/github/.bashrc     2>> /tmp/backup_dump
cp -r /home/pi/lobsang/*    /media/DRIVE/Lobsang/backup/            2>> /tmp/backup_dump
cp -r /home/pi/sketchbook/* /media/DRIVE/Lobsang/backup/sketchbook/ 2>> /tmp/backup_dump
cp    /home/pi/.bashrc      /media/DRIVE/Lobsang/backup/.bashrc     2>> /tmp/backup_dump

# Delete all files listed in .ignore from the USB stick's GitHub folder.
# Not all of the files need to be uploaded to GitHub. The backup folder
# on the USB stick contains every single file though.
if [ $verbose ] ; then
	echo -e "\tDeleting files in /media/DRIVE/github/ listed in .ignore"
fi
echo "Trying to delete usb files listed in .ignore..." >> /tmp/backup_dump
cd /media/DRIVE/Lobsang/github/
while read path; do
	rm -r $path 2>> /tmp/backup_dump
done < /home/pi/lobsang/.ignore

# Automatically remove the sensitive info from Padlock.py so I'm not
# telling the world the login keys to access Lobsang! I use 'sed -i'
# to change the file directly instead of eg. printing to the terminal.
echo "Trying to remove USB stick's passkeys in Padlock.py for GitHub..." >> /tmp/backup_dump
while read key; do
	if [ $verbose ] ; then
		echo "Removing passkeys from USB stick's GitHub Padlock.py"
	fi
	sed -i s/$key/****/ /media/DRIVE/Lobsang/github/Padlock.py 2>> /tmp/backup_dump
done < /home/pi/lobsang/.passkeys

if [ $verbose ] ; then
	echo "Transferred files."
fi

# If user has specified to list the content of /media/DRIVE/Lobsang/github
# with the argument "-l" or "--list", then do. Otherwise (auto) don't.
if [ $list_usb_folder ] ; then
	echo "Contents of /media/DRIVE/Lobsang/github/:"
	echo "Trying to list /media/DRIVE/Lobsang/github/..." >> /tmp/backup_dump
	ls /media/DRIVE/Lobsang/github/ 2>> /tmp/backup_dump
fi

if [ $verbose ] ; then
	echo "Waiting for 5 seconds in the hope that the USB stick will unmount after this time..."
	for value in `seq 0 5` ; do
		printf "Time before unmount begins: $((5-value))s \r"
		sleep 1
	done
	echo "USB stick should now co-operate."
else
	sleep 5
fi

# Unmount the USB stick
if [ $unmount_when_finished ] ; then
	echo "Trying to unmount..." >> /tmp/backup_dump
	sudo umount /media/DRIVE/ 2>> /tmp/backup_dump
	sudo rm -r /media/DRIVE/  2>> /tmp/backup_dump
fi

if [ $verbose ] ; then
	echo "It is should be safe to remove the USB stick now."
	echo "See file /tmp/backup_dump for error logging:"
	#cat /tmp/backup_dump
fi

# All finished!
exit 0
