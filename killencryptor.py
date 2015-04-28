import sys, traceback, os
import wmi

def encryptorTaskName():
	return 'Encryptor.exe'

def isEncryptorTaskRunning():
	c = wmi.WMI()
	for process in c.Win32_Process():
		if encryptorTaskName().lower() in process.Name.lower():
			return True
	return False

def killEncryptor():
	c = wmi.WMI()
	for process in c.Win32_Process():
		if encryptorTaskName().lower() in process.Name.lower():
			process.Terminate()

if __name__ == '__main__':
	print isEncryptorTaskRunning()
