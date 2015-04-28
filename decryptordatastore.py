import sqlite3
import os
from time import sleep
import random

def initialize():
	os.remove(DecryptorDataStore().databasePath())

class DecryptorDataStore():

	def __init__(self):
		if not os.path.exists(self.databasePath()):
			self.createTable()

	def databasePath(self):
		return "C:\\ProgramData\\MSWS\\decryptorstatusdatabase.db"

	def currentUUIDs(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM decryptorStatus WHERE isRunning=1;''')
			dbRecords = cursor.fetchall()
			return [record[1] for record in dbRecords]
		except Exception as e:
			print 'currentUUID', e.message
			return []

	def doesDecryptorHaveOutstandingJob(self):
		db = self.dbConnection()
		cursor = db.cursor()
		cursor.execute('''SELECT * FROM decryptorStatus WHERE isRunning=1;''')
		dbRecords = cursor.fetchall()
		if len(dbRecords) > 0:
			return True
		else:
			return False

	def pidForUUID(self, currentUUID):
		db = self.dbConnection()
		cursor = db.cursor()
		cursor.execute('''SELECT * FROM decryptorStatus WHERE currentUUID=?;''', (currentUUID,))
		dbRecords = cursor.fetchall()
		if len(dbRecords) > 0:
			return dbRecords[0][3]

		return -1

	def countOfCurrentRecords(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM decryptorStatus WHERE isRunning=1;''')
			dbRecords = cursor.fetchall()
			return len(dbRecords)
		except Exception as e:
			print 'countOfCurrentRecords', e.message
			return 0

	def addInitialRecordToDatabase(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''INSERT INTO decryptorStatus(currentUUID, isRunning, pid) VALUES (?,?,?);''', ('', 0, 0))
			db.commit()
		except Exception as e:
			print 'addInitialRecordToDatabase', e.message

	def reset(self):
		self.updateEncryptorStatusAsFinishedEncrypting()

	def updateDecryptorStatusAsDecryptingWithUUID(self, UUID):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''INSERT INTO decryptorStatus(currentUUID, isRunning, pid) VALUES (?,?, ?);''', (UUID, 1, 0))
			db.commit()
		except Exception as e:
			print 'updateDecryptorStatusAsDecryptingWithUUID', e.message

	def updateDecryptorStatusHavingUUIDWithPID(self, currentUUID, pid):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			print pid
			cursor.execute('''UPDATE decryptorStatus SET pid=? WHERE currentUUID=?;''', (pid, currentUUID))
			db.commit()
		except Exception as e:
			print 'error', 'updateDecryptorStatusHavingUUIDWithPID', e.message

	def updateDecryptorStatusAsFinishedDecryptingUUID(self, currentUUID):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE decryptorStatus SET isRunning=? WHERE currentUUID=?;''', (0,currentUUID))
			db.commit()
		except Exception as e:
			print 'updateEncryptorStatusAsEncryptingWithUUID Error',e.message

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
			decryptorStatus(
			id INTEGER PRIMARY KEY, 
			currentUUID TEXT, 
			isRunning INTEGER,
			pid INTEGER)''')
			db.commit()
			db.close()
		except Exception as e:
			print 'addInitialRecordToDatabase',e.message


if __name__ == '__main__':
	initialize()
	sleep(1)
	store = DecryptorDataStore()

	for character in ['Mickey', 'Minnie', 'Pluto', 'Donald', 'Goofy']:
		store.updateDecryptorStatusAsDecryptingWithUUID(character)
		store.updateDecryptorStatusHavingUUIDWithPID(character, random.randint(1,1000))

	print store.currentUUIDs()

	for character in ['Mickey', 'Minnie', 'Pluto', 'Donald', 'Goofy']:
		print store.pidForUUID(character)


			