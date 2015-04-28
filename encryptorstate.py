import os
import json
import subprocess
from threading import Thread
from Queue import Queue
from multiprocessing import Process
from time import sleep

from datastore import WSJob
from encryptorparser import EncryptorParser
from encryptordatastore import EncryptorDataStore

import killencryptor
from mediasealjobdata import xmlArgsFromCommandLineArgs

class EncryptorOptions():
	def __init__(self):

		configurationOptions = self.configurationOptions()

		self.encryptorApplicationPath = configurationOptions['encryptorApplicationPath']
		self.jobStatusOuputPath = configurationOptions['jobStatusOuputPath']
		self.templateID = configurationOptions['templateID']
		self.templateJobName = configurationOptions['templateJobName']
		self.username = configurationOptions['username']
		self.password = configurationOptions['password'] 
		self.inputPath = 'C:\\Path\\To\\Input\\Path'
		self.destinationPath = 'C:\\Path\\To\\Destination\\Path'

	def allKeys(self):
		return ['encryptorApplicationPath', 'jobStatusOuputPath', 'templateID', 'templateJobName', 'username', 'password']

	def pathKeys(self):
		return ['encryptorApplicationPath']

	def folderKeys(self):
		return ['jobStatusOuputPath']

	def configurationPath(self):
		return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'options.json')

	def configurationOptions(self):
		if not os.path.exists(self.configurationPath()):
			raise Exception('No configuration file found!!')

		configurationOptions = None
		errors = []
		with open(self.configurationPath(), 'r') as f:
			configurationOptions = json.loads(f.read())

		for element in self.allKeys():
			if element not in configurationOptions.keys():
				errors.append('Configuration Errors: No value found for %s' % (element))

		for element in self.pathKeys():
			if not os.path.exists(configurationOptions[element]):
				errors.append('Configuration Errors: No file found at path for %s' % (element))

		for element in self.folderKeys():
			if not os.path.exists(os.path.dirname(configurationOptions[element])):
				errors.append('Configuration Errors: No folder found at path for %s' % (element))

		if len(errors)>0:
			print "\n".join(errors)
			print "\n"

			raise Exception('Configuration Errors Found!!!!!')

		return configurationOptions

	def encryptorOptionsWithInputAssetAndDestinationFolder(self, inputAsset, destinationFolder):
		return [self.encryptorApplicationPath, '-o', self.jobStatusOuputPath, '-templateid', self.templateID, 
		'-templatejobname', self.templateJobName, '-outputpath', destinationFolder, '-u', self.username, 
		'-p', self.password, inputAsset]

class EncryptorStatusReader():
	def __init__(self, filePathToRead, messageQueue):
		self.queue = messageQueue
		self.filePathToRead = filePathToRead
		self.isRunning = True

		try:
			os.remove(filePathToRead)
		except Exception as e:
			print 'not deleting log file'

	def terminate(self):
		self.isRunning = False

	def run(self):
		while self.isRunning == True:
			sleep(0.5)
			if os.path.exists(self.filePathToRead):
				try:
					with open(self.filePathToRead, 'r') as f:
						contents = f.read()
						if contents is not None:
							self.queue.put(EncryptorParser(contents).progressInfo())
				except Exception as e:
					self.queue.put(e.message)

class EncryptorProcess():
	def __init__(self, arguments):

		useXMLMode = True

		if useXMLMode == True:
			self.args = xmlArgsFromCommandLineArgs(arguments)
		else:
			self.args = arguments

		self.isRunning = False
		self.returncode = 0

	def run(self):
		try:
			self.isRunning = True
			process = subprocess.Popen(self.args)
			out, err = process.communicate()
			self.returncode = process.returncode
		except Exception as e:
			self.returncode = -10

		self.isRunning = False

def encryptorAction(uuid):

	currentJob = WSJob(uuid=uuid)
	if currentJob == None:
		return 

	currentJob.willBeginEncrypting()

	sourceAsset, destinationFolder = currentJob.pathParameters()
	encryptorArguments = EncryptorOptions().encryptorOptionsWithInputAssetAndDestinationFolder(sourceAsset, destinationFolder)

	queue = Queue()
	encryptor 		= EncryptorProcess(encryptorArguments)
	reader 			= EncryptorStatusReader(EncryptorOptions().jobStatusOuputPath, queue)

	encryptThread	= Thread(target=encryptor.run)
	readerThread	= Thread(target=reader.run)

	encryptThread.start()
	readerThread.start()

	while encryptor.isRunning == True:
		sleep(0.5)
		if not queue.empty():
			infoDict = queue.get()
			currentJob.updateEncryptionStatusInfo(infoDict)

	while not queue.empty():
		infoDict = queue.get()
		currentJob.updateEncryptionStatusInfo(infoDict)

	currentJob.willFinishEncrypting()
	currentJob.willFinishWithReturnCode(encryptor.returncode)

	EncryptorDataStore().updateEncryptorStatusAsFinishedEncrypting()

	reader.terminate()


class EncryptorStatus(object):
	_instance = None
	process = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(EncryptorStatus, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def startEncryptingAsset(self, uuid):
		self.process = Process(target=encryptorAction, args=[uuid])
		self.process.start()
		EncryptorDataStore().updateEncryptorStatusAsEncryptingWithUUID(uuid)

	def stop(self, uuid):
		existingJob = WSJob(uuid=uuid)
		existingJob.willCancelEncryption()

		if killencryptor.isEncryptorTaskRunning() == True:
			killencryptor.killEncryptor()
			while killencryptor.isEncryptorTaskRunning() == True:
				sleep(0.5)

			print 'existingJob.didCancelEncryption()'
			existingJob.didCancelEncryption()
			print self.process.exitcode

		EncryptorDataStore().updateEncryptorStatusAsFinishedEncrypting()

	def isEncryptorRunningAJob(self):
		return EncryptorDataStore().doesEncryptorHaveOutstandingJob()

	def isEncryptorTaskRunning(self):
		return killencryptor.isEncryptorTaskRunning()

	def currentUUID(self):
		return EncryptorDataStore().currentUUID()

def identityTest():
	EncryptorOptions()

	s1=EncryptorStatus()
	s2=EncryptorStatus()

	if(id(s1)==id(s2)):
		print "Same"
	else:
		print "Different"

def encryptorTest():
	newJob = WSJob("F:\\Avid_DNxHD_Test_Movie.mov", 'F:\\')
	
	encryptor = EncryptorStatus()
	encryptor.startEncryptingAsset(newJob.uuid)
	easyTimer = 1

	while encryptor.isEncryptorRunningAJob() == True:
		newJob.refresh()
		print newJob.jsonStatus()
		sleep(1)

		easyTimer += 1
		if easyTimer == 90:
			print 'will kill job'
			encryptor.stop(newJob.uuid)

	newJob.refresh()
	print 'Finished:', newJob.jsonStatus()

if __name__ == '__main__':
	encryptorTest()


