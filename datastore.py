import sqlite3
import datetime
import os
from uuid import uuid1
import json
import time

#accepted 0
#begin encrypting 1
#finished encrypting 2
#will cancel -1
#cancelled -2

#operationType 0 is encryption, 1 is decryption

def initialize():
	WSJob(uuid='this will create the table if it does not exist')

class WSJob():

	@staticmethod
	def Decrypt():
		return 1

	@staticmethod
	def Encrypt():
		return 0

	@staticmethod
	def OperationCanceled():
		return -2

	@staticmethod
	def OperationComplete():
		return 2

	@staticmethod
	def isSourceAndDestinationFileAlreadyInUse(currentUUIDs, sourceFile, destinationFile):
		jobs = [WSJob(uuid=uuid) for uuid in currentUUIDs]
		for job in jobs:
			if job.sourcePath == sourceFile and job.destinationPath == destinationFile:
				return True
		return False

	def __init__(self, sourcePath='', destinationPath='', operationType=0, uuid=None):
		self.prepareDatabase()

		self.id 				= -1
		self.sourcePath 		= 'NOPATH'
		self.destinationPath 	= 'NOPATH'
		self.dateAdded 			= datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S")
		self.dateModified 		= datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S")
		self.operationStatus 	= -1
		self.statusInformation 	= json.dumps({'totalProgress':'0', 'lastLogItem':'None'})
		self.operationType 		= -1
		self.uuid 				= uuid
		self.dateStarted 		= datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S")
		self.dateFinished 		= datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S")
		self.returnCode			= -1
		self.elapsedTime		= 0

		if uuid == None:
			self.sourcePath 		= sourcePath
			self.destinationPath 	= destinationPath
			self.operationType 		= operationType

			self.uuid = str(uuid1().int)
			self.dateAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.dateModified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.addJobToDatabase(self.sourcePath, self.destinationPath, self.dateAdded, self.dateModified, self.uuid, self.operationType)

		existingRecord = self.retrieveRecordForUUID(self.uuid)
		if existingRecord == None:
			return

		self.id					= existingRecord[0]
		self.sourcePath 		= existingRecord[1]
		self.destinationPath 	= existingRecord[2]
		self.dateAdded 			= existingRecord[3]
		self.dateModified 		= existingRecord[4]
		self.operationStatus 	= existingRecord[5]
		self.statusInformation 	= existingRecord[6]
		self.operationType 		= existingRecord[7]
		self.uuid 				= existingRecord[8]
		self.dateStarted		= existingRecord[9]
		self.dateFinished		= existingRecord[10]
		self.returnCode			= existingRecord[11]
		self.elapsedTime		= existingRecord[12]


	def refresh(self):
		#useful for when using the data across multiple processes
		existingRecord = self.retrieveRecordForUUID(self.uuid)
		if existingRecord == None:
			return

		self.id					= existingRecord[0]
		self.sourcePath 		= existingRecord[1]
		self.destinationPath 	= existingRecord[2]
		self.dateAdded 			= existingRecord[3]
		self.dateModified 		= existingRecord[4]
		self.operationStatus 	= existingRecord[5]
		self.statusInformation 	= existingRecord[6]
		self.operationType 		= existingRecord[7]
		self.uuid 				= existingRecord[8]
		self.dateStarted		= existingRecord[9]
		self.dateFinished		= existingRecord[10]
		self.returnCode			= existingRecord[11]
		self.elapsedTime		= existingRecord[12]

	def prepareDatabase(self):
		dbFolder = os.path.basename(self.databasePath())

		if not os.path.exists(dbFolder):
			try:
				os.mkdir(dbFolder)
			except Exception as e:
				print e.message

		if not os.path.exists(self.databasePath()):
			self.createTable()

	def jobNotFound(self):
		if self.id == -1:
			return True
		return False

	def databasePath(self):
		return "C:\\ProgramData\\MSWS\\database.db"

	def retrieveRecordForUUID(self, uuid):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM dataTable WHERE uuid=?''', (uuid,))
			dbRecords = cursor.fetchall()
			if len(dbRecords) > 0:
				record = dbRecords[0]
				return record
		except Exception as e:
			print e.message

			return tuple([])

	def addJobToDatabase(self, sourcePath, destinationPath, dateAdded, dateModified, uuid, operationType):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''INSERT INTO dataTable(
			    sourcePath, 
			    destinationPath, 
			    dateAdded,
			    dateModified,  
			    operationStatus, 
			    statusInformation,
			    operationType,
			    uuid,
			    dateStarted,
			    dateFinished, 
			    returnCode,
			    elapsedTime) 
			VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (
				sourcePath, 
				destinationPath, 
				dateAdded, 
				dateModified,
				0,
				'{}',
				operationType,
				uuid,
				datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S"),
				datetime.datetime(2000,1,1).strftime("%Y-%m-%d %H:%M:%S"),
				-100,
				0
				)
			)
			db.commit()
		except Exception as e:
			print e.message

	def willCancelEncryption(self):
		self.willFinishWithOperationStatus(-1)

	def didCancelEncryption(self):
		self.willFinishWithOperationStatus(-2)

	def willFinishEncrypting(self):
		self.willFinishWithOperationStatus(2)

	def willCancelDecryption(self):
		self.willFinishWithOperationStatus(-1)

	def didCancelDecryption(self):
		self.willFinishWithOperationStatus(-2)

	def willFinishDecrypting(self):
		self.willFinishWithOperationStatus(2)

	def willFinishWithOperationStatus(self, operationStatus):
		try:
			self.dateFinished = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.operationStatus = operationStatus

			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE dataTable SET dateFinished=?, operationStatus=? WHERE id=?;''', (
				self.dateFinished, self.operationStatus, self.id))
			db.commit()
		except Exception as e:
			print 'willFinishWithOperationStatus Error',e.message

	def willFinishWithReturnCode(self, returnCode):
		try:
			self.dateFinished = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.returnCode = returnCode

			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE dataTable SET dateFinished=?, returnCode=? WHERE id=?;''', (
				self.dateFinished, self.returnCode, self.id))
			db.commit()
		except Exception as e:
			print 'willFinishWithReturnCode Error',e.message

	def willBeginEncrypting(self):
		self.willBeginOperation()

	def willBeginDecrypting(self):
		self.willBeginOperation()

	def willBeginOperation(self):
		try:
			self.dateStarted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.operationStatus = 1

			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE dataTable SET dateStarted=?, operationStatus=? WHERE id=?;''', (
				self.dateStarted,self.operationStatus, self.id))
			db.commit()
		except Exception as e:
			print 'willBeginEncrypting Error', e.message

	def updateEncryptionStatusInfo(self, nStatusInformation):
		try:
			self.statusInformation = nStatusInformation
			statusInfoObject = json.loads(self.statusInformation)

			db = self.dbConnection()
			db = self.dbConnection()
			cursor = db.cursor()

			if 'totalProgress' in statusInfoObject and statusInfoObject['totalProgress'] == str(1):
				self.elapsedTime = time.time()
				cursor.execute('''UPDATE dataTable SET statusInformation=?, elapsedTime=? WHERE id=?;''', (nStatusInformation, self.elapsedTime, self.id))
			else:
				cursor.execute('''UPDATE dataTable SET statusInformation=? WHERE id=?;''', (nStatusInformation , self.id))
			
			db.commit()

		except Exception as e:
			print 'updateEncryptionStatusInfo Error',e.message

	def updateDecryptionStatusInfo(self, nStatusInformation):
		try:
			self.statusInformation = nStatusInformation
			statusInfoObject = json.loads(self.statusInformation)
			

			db = self.dbConnection()
			db = self.dbConnection()
			cursor = db.cursor()

			if self.elapsedTime == 0:
				self.elapsedTime = time.time()
				cursor.execute('''UPDATE dataTable SET statusInformation=?, elapsedTime=? WHERE id=?;''', (nStatusInformation, self.elapsedTime, self.id))
			else:
				cursor.execute('''UPDATE dataTable SET statusInformation=? WHERE id=?;''', (nStatusInformation , self.id))

			db.commit()

		except Exception as e:
			print 'updateDecryptionStatusInfo', e.message

	def timeRemaining(self):
		if self.operationType == WSJob.Encrypt():
			return self.calculateTimeRemainingEncryption()

		return self.calculateTimeRemainingDecryption()

	def calculateTimeRemainingEncryption(self):
		data = json.loads(self.statusInformation)

		try:
			if data['totalProgress'] == str(0):
				return '-1'
		except Exception as e:
			print 'error',e.message
			return '-1'

		if self.operationStatus == 2:
			return "{:2.2f}".format(0)

		timeConsumedPerIncrement = float(time.time() - self.elapsedTime) / int(data['totalProgress'])
		incrementRemaining = 100 - int(data['totalProgress'])
		return "{:2.2f}".format(timeConsumedPerIncrement * incrementRemaining)

	def calculateTimeRemainingDecryption(self):
		data = json.loads(self.statusInformation)
		if 'dataRead' not in data:
			return "{:2.2f}".format(0)

		if not os.path.exists(self.destinationPath):
			return "{:2.2f}".format(0)

		dataWritten = os.path.getsize(self.destinationPath)
		dataTotalToRead = os.path.getsize(self.sourcePath)

		try:
			timeConsumedPerIncrement = (time.time() - self.elapsedTime)/float(dataWritten)
		except Exception as e:
			timeConsumedPerIncrement = 0

		incrementRemaining = dataTotalToRead - dataWritten
		return "{:2.2f}".format(timeConsumedPerIncrement * incrementRemaining)

	def decryptionPercentageComplete(self):
		if not os.path.exists(self.destinationPath):
			return 0.0

		dataWritten = os.path.getsize(self.destinationPath)
		dataTotalToRead = os.path.getsize(self.sourcePath)
		return float(dataWritten)/dataTotalToRead * 100

	def jsonStatus(self):
		data = json.loads(self.statusInformation)
		data['returnCode'] = self.returnCode
		data['timeRemaining'] = self.timeRemaining()
		data['operationStatus'] = self.operationStatus

		if 'lastLogItem' not in data:
			if self.operationType == WSJob.Encrypt():
				data['lastLogItem'] = 'Starting Encryption.'
			else:
				if self.operationStatus == -2:
					data['lastLogItem'] = 'Decryption was cancelled.'
				elif self.operationStatus == 2:
					data['lastLogItem'] = 'Decryption has finished.'
				elif self.operationStatus == -1:
					data['lastLogItem'] = 'Decryption is being cancelled.'
				else:
					data['lastLogItem'] = 'Decrypting File.'

		if 'totalProgress' not in data:
			if self.operationType == WSJob.Encrypt():
				data['totalProgress'] = '0'
			else:
				data['totalProgress'] = "{:2.2f}".format(self.decryptionPercentageComplete())

		if 'dataRead' in data:
			del data['dataRead']

		data['sourceFile'] = self.sourcePath

		if self.operationType == WSJob.Encrypt():
			data['destinationFile'] = os.path.join(self.destinationPath, os.path.basename(self.sourcePath))
		else:
			data['destinationFile'] = self.destinationPath

		return json.dumps(data)

	def cleanUpCancelledDecryptionFile(self):
		try:
			os.remove(self.destinationPath)
		except Exception as e:
			print e.message

	def wasJobCancelled(self):
		if self.operationStatus == WSJob.OperationCanceled():
			return True
		return False

	def pathParameters(self):
		return tuple([self.sourcePath, self.destinationPath])

	def dbConnection(self):
		localdb = None
		try:
			localdb = sqlite3.connect(self.databasePath())
			return localdb
		except Exception as e:
			print e.message

	def createTable(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS 
			dataTable(
			id INTEGER PRIMARY KEY, 
			sourcePath TEXT, 
			destinationPath TEXT,
			dateAdded DATETIME, 
			dateModified DATETIME, 
			operationStatus INTEGER,  
			statusInformation TEXT,
			operationType INTEGER,
			uuid TEXT,
			dateStarted DATETIME, 
			dateFinished DATETIME,
			returnCode INTEGER,
			elapsedTime INTEGER)''')
			db.commit()
			db.close()
		except Exception as e:
			print e.message

			