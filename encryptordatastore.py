import sqlite3
import os
from time import sleep

def initialize():
	EncryptorDataStore().reset()

class EncryptorDataStore():

	def __init__(self):
		if not os.path.exists(self.databasePath()):
			self.createTable()
		if self.countOfCurrentRecords() == 0:
			self.addInitialRecordToDatabase()

	def databasePath(self):
		return "C:\\ProgramData\\MSWS\\encryptorstatusdatabase.db"

	def currentUUID(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM encryptorStatus;''')
			dbRecords = cursor.fetchall()
			if len(dbRecords) > 0:
				record = dbRecords[0]
				return record[1]
		except Exception as e:
			print 'currentUUID', e.message
			return ''

	def doesEncryptorHaveOutstandingJob(self):
		db = self.dbConnection()
		cursor = db.cursor()
		cursor.execute('''SELECT * FROM encryptorStatus;''')
		dbRecords = cursor.fetchall()
		if len(dbRecords) > 0:
			record = dbRecords[0]
			if record[2] == 1:
				return True
			else:
				return False

	def countOfCurrentRecords(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM encryptorStatus;''')
			dbRecords = cursor.fetchall()
			return len(dbRecords)
		except Exception as e:
			print 'countOfCurrentRecords', e.message
			return 0

	def addInitialRecordToDatabase(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''INSERT INTO encryptorStatus(currentUUID, isRunning) VALUES (?,?);''', ('', 0))
			db.commit()
		except Exception as e:
			print 'addInitialRecordToDatabase', e.message

	def reset(self):
		self.updateEncryptorStatusAsFinishedEncrypting()

	def updateEncryptorStatusAsEncryptingWithUUID(self, UUID):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE encryptorStatus SET currentUUID=?, isRunning=? WHERE id=?;''', (UUID,1,1))
			db.commit()
		except Exception as e:
			print 'updateEncryptorStatusAsEncryptingWithUUID Error',e.message

	def updateEncryptorStatusAsFinishedEncrypting(self):
		try:
			db = self.dbConnection()
			cursor = db.cursor()
			cursor.execute('''UPDATE encryptorStatus SET currentUUID=?, isRunning=? WHERE id=?;''', ('',0,1))
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
			encryptorStatus(
			id INTEGER PRIMARY KEY, 
			currentUUID TEXT, 
			isRunning INTEGER)''')
			db.commit()
			db.close()
		except Exception as e:
			print 'addInitialRecordToDatabase',e.message


if __name__ == '__main__':
	store = EncryptorDataStore()
	store.updateEncryptorStatusAsEncryptingWithUUID('Mickey Mouse')
	sleep(20)
	store.updateEncryptorStatusAsFinishedEncrypting()
			