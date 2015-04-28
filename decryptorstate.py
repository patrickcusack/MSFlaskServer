import os
import json
import subprocess
from threading import Thread
from Queue import Queue
from multiprocessing import Process
from time import sleep

from datastore import WSJob
from decryptordatastore import DecryptorDataStore
from decryptoroptions import DecryptorOptions

import killdecryptor

class DecryptorStatusReader():
	def __init__(self, filePathToRead, messageQueue):
		self.queue = messageQueue
		self.filePathToRead = filePathToRead
		self.isRunning = True

	def terminate(self):
		self.isRunning = False

	def run(self):
		while self.isRunning == True:
			sleep(0.5)
			if os.path.exists(self.filePathToRead):
				size = os.path.getsize(self.filePathToRead)
				self.queue.put(json.dumps({'dataRead':size}))

class DecryptorProcess():
	def __init__(self, arguments, uuid):

		self.args = arguments
		self.isRunning = False
		self.returncode = 0
		self.uuid = uuid

	def run(self):
		try:
			self.isRunning = True
			process = subprocess.Popen(self.args)
			DecryptorDataStore().updateDecryptorStatusHavingUUIDWithPID(self.uuid, process.pid)
			out, err = process.communicate()
			self.returncode = process.returncode
		except Exception as e:
			self.returncode = -10

		self.isRunning = False

def decryptorAction(uuid):

	currentJob = WSJob(uuid=uuid)
	if currentJob == None:
		return 

	currentJob.willBeginDecrypting()

	sourceAsset, destinationFile = currentJob.pathParameters()
	decryptorArguments = DecryptorOptions().decryptorOptionsWithInputAssetAndDestinationFile(sourceAsset, destinationFile)

	queue = Queue()
	decryptor 		= DecryptorProcess(decryptorArguments, uuid)
	reader 			= DecryptorStatusReader(destinationFile, queue)

	encryptThread	= Thread(target=decryptor.run)
	readerThread	= Thread(target=reader.run)

	encryptThread.start()
	readerThread.start()

	while decryptor.isRunning == True:
		sleep(0.5)
		if not queue.empty():
			infoDict = queue.get()
			currentJob.updateDecryptionStatusInfo(infoDict)

	while not queue.empty():
		infoDict = queue.get()
		currentJob.updateDecryptionStatusInfo(infoDict)

	currentJob.willFinishDecrypting()
	currentJob.willFinishWithReturnCode(decryptor.returncode)
	DecryptorDataStore().updateDecryptorStatusAsFinishedDecryptingUUID(uuid)

	reader.terminate()


class DecryptorStatus(object):
	_instance = None
	process = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(DecryptorStatus, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def startDecryptingAsset(self, uuid):
		self.process = Process(target=decryptorAction, args=[uuid])
		self.process.start()
		DecryptorDataStore().updateDecryptorStatusAsDecryptingWithUUID(uuid)

	def stop(self, uuid):
		existingJob = WSJob(uuid=uuid)
		existingJob.willCancelDecryption()

		if uuid in DecryptorDataStore().currentUUIDs():
			pid = DecryptorDataStore().pidForUUID(uuid)
			killdecryptor.killDecryptorWithPID(pid)
			while killdecryptor.isDecryptorTaskRunningWithPID(pid) == True:
				sleep(0.5)

			existingJob.didCancelDecryption()
			existingJob.cleanUpCancelledDecryptionFile()

		DecryptorDataStore().updateDecryptorStatusAsFinishedDecryptingUUID(uuid)

	def isDecryptorRunningAJob(self):
		runningjobs = DecryptorDataStore().currentUUIDs()
		if len(runningjobs) > 0:
			return True
		return False

	def slotsAvailable(self):
		runningjobs = DecryptorDataStore().currentUUIDs()
		return DecryptorOptions().decryptorSlots - len(runningjobs)

	def currentUUIDs(self):
		return DecryptorDataStore().currentUUIDs()

def identityTest():
	DecryptorOptions()

	s1=DecryptorStatus()
	s2=DecryptorStatus()

	if(id(s1)==id(s2)):
		print "Same"
	else:
		print "Different"

def decryptorTest():
	newJob = WSJob("F:\\Avid_DNxHD_Test_Movie-enc.mov", 'F:\\temp', operationType=1)
	
	decryptorStatus = DecryptorStatus()
	decryptorStatus.startDecryptingAsset(newJob.uuid)
	easyTimer = 1

	print decryptorStatus.currentUUIDs()
	while newJob.uuid in decryptorStatus.currentUUIDs():
		print 'new job in uuids'
		newJob.refresh()
		print newJob.jsonStatus()
		sleep(1)

		# easyTimer += 1
		# if easyTimer == 90:
		# 	print 'will kill job'
		# 	decryptorStatus.stop(newJob.uuid)


	newJob.refresh()
	print 'Finished:', newJob.jsonStatus()

if __name__ == '__main__':
	# applicationPath = "C:\\Program Files (x86)\\MediaSeal\\DeArchiver\\DeArchiver.exe"
	# DecryptorProcess([applicationPath, "F:\\Avid_DNxHD_Test_Movie-enc.mov", "F:\\temp\\test.mov"]).run()
	# decryptorAction('MickeyMouse')
	decryptorTest()
	print DecryptorStatus().slotsAvailable

