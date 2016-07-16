import psutil
import subprocess

for process in psutil.process_iter():
	if process.cmdline == ['sudo', 'python', 'nndist.py']:
		print('Process found. Terminating it.')
		process.terminate()
		break
else:
    print('Process not found: starting it.')
    subprocess.Popen(['sudo', 'python', 'nndist.py'])