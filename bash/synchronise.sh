#!/bin/bash
#
# synchronise(.sh)-  mounts, copies, syncs and unmounts USB stick. As the
# Pi A+ has only one USB port, copying data is somewhat  difficult.  This
# script runs every time you plug in the USB stick and almost  instantly.
# Udev notices hotplugging and the rule file in  /etc/udev/rules.d/  runs
# this script which copies over all the data and code in /home/pi/lobsang
# and a few other places for adding to the git repository or just general
# backing up. A complete backup is made on the drive in  /Losbang/backup/
# including files that don't get  copied to the /Lobsang/github/  folder.
# Files  to ignore  are  put in /home/pi/lobsang/.ignore  and do not  get
# copied to the drive's /Lobsang/github folder, similar to the .gitignore
# file (that is where the idea came from).
#
# Command-line arguments are: -e to open the file for editing using nano.
# When you save and close the file, it is  automatically  updated in both
# /usr/bin/synchronise and /home/pi/lobsang/bash/
#
# -u or --update copies the file /home/pi/lobsang/bash/synchronise.sh  to
# /usr/bin/synchronise. This is just to make it easier for the  end user.
# It's not too  hard to sudo cp...
#
# -a or --auto make the synchronise script run automatically when the USB
# drive is plugged in.   See /etc/udev/rules.d/10-lobsang_auto_sync.rules
# for the rule file that does the hotplug noticing  and runs this script.
#
# -n or --no-auto to disable the above feature. Basically it just renames
# the rule file so it doesn't have the .rules extension so udev does  not
# see the file and therefore does not ever run this script.
#
# Please note the >> $LOG (and variations of this) to the right hand side
# of the script lines.  All processes  that might go wrong  and output an
# error send it to this file, plus extra info this script writes in  case
# anything goes wrong. Each time this script is run, any previous data is
# overwritten in the log file.
#
# Created July 2016 by Finley Watson.

# The file that all info is dumped to.
LOG=/tmp/synchronise_dump

# A crude way of checking for command line arguments.
if [ -n "$1" ] ; then
	if [ "$1" == "-e" ] || [ "$1" == "--edit" ] ; then
		echo "Opening synchronise file for editing..."
		nano /home/pi/lobsang/bash/synchronise.sh
		sudo /home/pi/lobsang/bash/synchronise.sh -u
		echo "Updated file."
		exit 0
	elif [ "$1" == "-u" ] || [ "$1" == "--update" ] ; then
		echo "Updating /usr/bin/synchronise to the latest synchronise file in /home/pi/lobsang/bash/..."
		sudo cp /home/pi/lobsang/bash/synchronise.sh /usr/bin/synchronise
		exit 0
	elif [ "$1" == "-a" ] || [ "$1" == "--auto" ] ; then
		sudo mv /etc/udev/rules.d/10-lobsang_auto_sync.disabled /etc/udev/rules.d/10-lobsang_auto_sync.rules
		sudo udevadm control --reload-rules
		exit 0
	elif [ "$1" == "-n" ] || [ "$1" == "--no-auto" ] ; then
		sudo mv /etc/udev/rules.d/10-lobsang_auto_sync.rules /etc/udev/rules.d/10-lobsang_auto_sync.disabled
		sudo udevadm control --reload-rules
		exit 0
	fi
fi

# Backup has started. Make the Duino LED blink quickly to show this.
cd /home/pi/lobsang/
sudo python -c "import Lobsang; Lobsang.file_sync_started()"

# Clear the dump file of old data.
echo "File in which all error output from /usr/bin/synchronise is dumped"			  > $LOG

# Mount the USB stick called FORCE on /mnt/ .
echo "Trying to mount usb stick..."	 						 >> $LOG
sudo mount -t vfat LABEL=FORCE /mnt/							2>> $LOG

# Just in case the directories don't exist on the drive, try to create them.
echo "Trying to create directories that should already exist..."			 >> $LOG
sudo mkdir /mnt/Lobsang/								2>> $LOG
sudo mkdir /mnt/Lobsang/github/								2>> $LOG
sudo mkdir /mnt/Lobsang/github/sketchbook/						2>> $LOG
sudo mkdir /mnt/Lobsang/backup/		 						2>> $LOG
sudo mkdir /mnt/Lobsang/backup/sketchbook/						2>> $LOG
sudo mkdir /mnt/Lobsang/install/							2>> $LOG

# Copy over all the files to be backed up.
echo "Trying to copy over all files..."							 >> $LOG
cp -fr /home/pi/lobsang/*				/mnt/Lobsang/github/		2>> $LOG
cp -fr /home/pi/sketchbook/*				/mnt/Lobsang/github/sketchbook/ 2>> $LOG
cp -f  /etc/udev/rules.d/10-lobsang_auto_sync.*		/mnt/Lobsang/github/		2>> $LOG
cp -fr /home/pi/lobsang/*				/mnt/Lobsang/backup/		2>> $LOG
cp -fr /home/pi/sketchbook/*				/mnt/Lobsang/backup/sketchbook/	2>> $LOG
cp -f  /etc/udev/rules.d/10-lobsang_auto_sync.*		/mnt/Lobsang/backup/		2>> $LOG

# Delete all files listed in .ignore from the USB stick's GitHub folder.
# Not all of the files need to be uploaded to GitHub. The backup folder
# on the USB stick contains every single file though, excluding *.pyc.
echo "Trying to delete files in drive's GitHub folder listed in .ignore..."		 >> $LOG
cd /mnt/Lobsang/github/
while read path; do
	rm -r $path									2>> $LOG
done < /home/pi/lobsang/.ignore

# Remove the .pyc compiled python code from the frive - it's not required.
echo "Trying to remove drive's *.pyc files from Backup folder..."			 >> $LOG
cd /mnt/Lobsang/backup/
sudo rm *.pyc

# Automatically remove the sensitive info from Padlock.py so I'm not
# telling the world the login keys to access Lobsang! I use  sed -i
# to change the file directly instead of eg. printing to the terminal.
echo "Trying to remove drive's passkeys in Padlock.py in GitHub folder..."		 >> $LOG
while read key; do
	sed -i s/$key/****/ /mnt/Lobsang/github/Padlock.py				2>> $LOG
done < /home/pi/lobsang/.passkeys

# Ought to flush cached cp data (this may not be necessary).
sync

# Move any files in  /mnt/Lobsang/install/  to  /home/pi/lobsang/
# but if there is a pre-existing file then back that one up first.
sudo mv --backup=simple /mnt/Lobsang/install/* /home/pi/lobsang/			2>> $LOG

# List the complete contents of the usb stick's directory /Lobsang/
echo "Contents of /mnt/Lobsang/ are:"							 >> $LOG
ls /mnt/Lobsang/*								 	 >> $LOG
echo "Contents end."									 >> $LOG

# Unmount the USB stick.
echo "Trying to unmount..."								 >> $LOG
sudo umount -l /mnt/									2>> $LOG
echo "Unmounted."									 >> $LOG

# Backup has finished. Make the Duino LED blink reqularly again to show this.
cd /home/pi/lobsang/
sudo python -c "import Lobsang; Lobsang.file_sync_finished()"

exit 0
