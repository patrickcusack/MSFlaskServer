import sys, traceback, os
import wmi
import subprocess

def decryptorTaskName():
	return 'DeArchiver'

def isDecryptorTaskRunningWithPID(pid):
	c = wmi.WMI()
	for process in c.Win32_Process():
		if decryptorTaskName().lower() in process.Name.lower() and pid == process.ProcessID:
			return True
	return False

def killDecryptorWithPID(pid):
	c = wmi.WMI()
	for process in c.Win32_Process():
		if decryptorTaskName().lower() in process.Name.lower() and pid == process.ProcessID:
			process.Terminate()

if __name__ == '__main__':
	applicationPath = "C:\\Program Files (x86)\\MediaSeal\\DeArchiver\\DeArchiver.exe"
	if not os.path.exists(applicationPath):
		print 'no application path'

	process = subprocess.Popen([applicationPath, "F:\\Avid_DNxHD_Test_Movie-enc.mov", "F:\\temp\\test.mov"])
	
	while process.poll() == None:
		print isDecryptorTaskRunningWithPID(process.pid)

	out, err = process.communicate()


