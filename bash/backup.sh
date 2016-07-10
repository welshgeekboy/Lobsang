#!/bin/bash
#
# backup(.sh)- will mount, copy data to
# then  unmount  my  USB stick.  As the
# Pi A+ has only one USB port,  copying
# data  is   somewhat  difficult.  This
# script runs  every  time you  plug in
# the USB stick, almost instantly. Udev
# notices hotplugging and the rule file
# in   /etc/udev/rules.d/   runs   this
# script which copies over all the data
# and code on Lobsang for adding to the
# git   repository,   or  just  general
# backing  up.  A  complete  backup  is
# created  in  Backup  including  files
# that  don't get copied  to the GitHub
# folder.  Files  to  ignore are put in
# /home/pi/lobsang/.ignore  and do  not
# get copied  to the  GitHub folder.
#
# Command-line  arguments  are:  -e  to
# open the file for  editing.  When you
# save  and  close  the  file,   it  is
# automatically  updated  in  /usr/bin/
# and /home/pi/lobsang/bash/
#
# [ TODO ] add the other args' info.
#
# Created July 2016 by Finley Watson.


# Possible command line arguments (all 0 or 1)
# When they have nothing after '=' sign they are false.
# list_usb_folder prints the contents of /mnt/Lobsang/github (auto off)
# delay toggles the 10s delay (auto on)
# unmount_when_finished will unmount the drive if 1 (auto on)
# verbose prints info as the copying occurs (auto on)
list_usb_folder=
delay=1
unmount_when_finished=1
verbose=1

# The file that info is dumped to.
LOG=/tmp/backup_dump

# A crude way of checking for command line arguments.
if [ -n "$1" ] ; then
	if [ "$1" == "-u" ] || [ "$1" == "-update" ] ; then
		echo "Updating /usr/bin/backup to the latest backup file in /home/pi/lobsang/bash/..."
		sudo cp /home/pi/lobsang/bash/backup.sh /usr/bin/backup
		exit 0
	elif [ "$1" == "-e" ] || [ "$1" == "--edit" ] ; then
		echo "Opening backup file for editing..."
		nano /home/pi/lobsang/bash/backup.sh
		sudo /home/pi/lobsang/bash/backup.sh -u
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
	elif [ "$1" == "-n" ] || [ "$1" == "--no-auto" ] ; then
		sudo mv /etc/udev/rules.d/10-lobsang_auto_sync.rules /etc/udev/rules.d/10-lobsang_auto_sync.disabled
		sudo udevadm control --reload-rules
		exit 0
	elif [ "$1" == "-a" ] || [ "$1" == "--auto" ] ; then
		sudo mv /etc/udev/rules.d/10-lobsang_auto_sync.disabled /etc/udev/rules.d/10-lobsang_auto_sync.rules
		sudo udevadm control --reload-rules
		exit 0
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

# Backup has started. Make the Duino LED blink quickly to show this.
dir=$PWD
cd /home/pi/lobsang
sudo python -c "import Lobsang; Lobsang.file_sync_started()"
cd $dir

echo "-------------------------------------"
echo " "
ps -e >> ~/loggity

# Give enough time for the USB drive to have been automatically mounted.
sleep 10

echo "-------------------------------------"
echo " "
ps -e >> ~/loggity

# Clear the dump file of old data.
echo "File in which all error output from /bin/backup is dumped" >> $LOG

# Mount the USB stick.
echo "Trying to mount usb stick..."	 >> $LOG
sudo mount /mnt/			2>> $LOG

echo "Contents of /mnt/ are:" >> $LOG
sleep 2
ls /mnt >> $LOG
echo "Contents end." >> $LOG
sleep 2

# Just in case the directories don't exist on the drive, try to create them.
echo "Trying to create directories that should already exist..."	 >> $LOG
sudo mkdir /mnt/Lobsang/                 				2>> $LOG
sudo mkdir /mnt/Lobsang/github/            				2>> $LOG
sudo mkdir /mnt/Lobsang/github/sketchbook/				2>> $LOG
sudo mkdir /mnt/Lobsang/backup/		 				2>> $LOG
sudo mkdir /mnt/Lobsang/backup/sketchbook/				2>> $LOG

# Copy over all the all files to be backed up.
echo "Trying to copy over all files..."							 >> $LOG
cp -r /home/pi/lobsang/*				/mnt/Lobsang/github/		2>> $LOG
cp -r /home/pi/sketchbook/*				/mnt/Lobsang/github/sketchbook/ 2>> $LOG
cp    /home/pi/.bashrc					/mnt/Lobsang/github/.bashrc	2>> $LOG
cp    /etc/udev/rules.d/10-lobsang_auto_sync.*		/mnt/Lobsang/github/		2>> $LOG
cp -r /home/pi/lobsang/*				/mnt/Lobsang/backup/		2>> $LOG
cp -r /home/pi/sketchbook/*				/mnt/Lobsang/backup/sketchbook/	2>> $LOG
cp    /home/pi/.bashrc					/mnt/Lobsang/backup/.bashrc	2>> $LOG
cp    /etc/udev/rules.d/10-lobsang_auto_sync.*		/mnt/Lobsang/backup/		2>> $LOG

# Delete all files listed in .ignore from the USB stick's GitHub folder.
# Not all of the files need to be uploaded to GitHub. The backup folder
# on the USB stick contains every single file though, excluding *.pyc.
echo "Trying to delete files in drive's GitHub folder listed in .ignore..." >> $LOG
cd /mnt/Lobsang/github/
while read path; do
	rm -r $path 2>> $LOG
done < /home/pi/lobsang/.ignore

echo "Trying to remove drive's *.pyc files from Backup folder..." >> $LOG
cd /mnt/Lobsang/backup/
sudo rm *.pyc

# Automatically remove the sensitive info from Padlock.py so I'm not
# telling the world the login keys to access Lobsang! I use 'sed -i'
# to change the file directly instead of eg. printing to the terminal.
echo "Trying to remove drive's passkeys in Padlock.py in GitHub folder..." >> $LOG
while read key; do
	sed -i s/$key/****/ /mnt/Lobsang/github/Padlock.py 2>> $LOG
done < /home/pi/lobsang/.passkeys

# If user has specified to list the content of /mnt/Lobsang/github
# with the argument "-l" or "--list", then do. Otherwise (auto) don't.
if [ $list_usb_folder ] ; then
	echo "Contents of /mnt/Lobsang/github/:" >> $LOG
	ls /mnt/Lobsang/github/ 		2>> $LOG
fi

sleep 1

echo "-------------------------------------"
echo " "
ps -e >> ~/loggity

fuser -a /mnt/ >> $LOG

# Unmount the USB stick
echo "Trying to unmount..." >> $LOG
sudo umount /mnt/	   2>> $LOG

fuser -a /mnt/ >> $LOG

# Backup has finished. Make the Duino LED blink reqularly again to show this.
dir=$PWD
cd /home/pi/lobsang
sudo python -c "import Lobsang; Lobsang.file_sync_finished()"
cd $dir

echo "-------------------------------------"
echo " "
ps -e >> ~/loggity

for i in `seq 1 11` ; do
	sleep 5
	echo "Check number $i of 10:"	>> $LOG
	echo " "			>> $LOG
	fuser -a /mnt/ >> $LOG
done

# All finished!
exit 0
