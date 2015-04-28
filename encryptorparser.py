import os
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
import xml.etree.cElementTree as ET
from xml.etree.cElementTree import ParseError
import json

class EncryptorParser():
	"""parse encryptor string output"""

	@staticmethod
	def isEncryptorStatusMessage(xmlString):
		try:
			parser = parseString(xmlString)
			if len(parser.getElementsByTagName("Status")) > 0:
				return True
			else:
				return False
		except ExpatError:
			return False

	def __init__(self, xmlString):

		tree = None
		try:
			tree = ET.fromstring(xmlString)
		except ParseError:
			self.datarate = 'no data'
			self.filebeingencrypted = 'no data'
			self.taskprogress = 'no data'
			self.totalprogress = 'no data'
			self.logentrycount = 'no data'
			self.xmlString = "ParserError"
			self.lastLogEntry = 'no data'

		if tree is not None:
			try:
				self.datarate = tree[0][0].text
				self.filebeingencrypted = tree[0][1].text
				self.taskprogress = tree[0][3].text
				self.totalprogress = tree[0][4].text
				self.logentrycount = 0
				self.xmlString = xmlString
				self.lastLogEntry = tree[0][2][-1].text
			except IndexError:
				self.datarate = 'no data'
				self.filebeingencrypted = 'no data'
				self.taskprogress = 'no data'
				self.totalprogress = 'no data'
				self.logentrycount = 'no data'
				self.xmlString = 'no data'
				self.lastLogEntry = 'no data'

	def parsedString(self):
		return "{0}\t{1}\t{2}\t{3}\t{4}".format(self.totalprogress, self.taskprogress, self.datarate, self.logentrycount, self.filebeingencrypted)

	def parsedDictionary(self):
		return {'totalprogress':self.totalprogress, 'taskprogress':self.taskprogress, 'datarate':self.datarate, 'logentrycount':self.logentrycount, 'filebeingencrypted':self.filebeingencrypted}

	def shortStatusString(self):
		filebeingencrypted = self.filebeingencrypted
		totalprogress = self.totalprogress
		if filebeingencrypted == None:
			filebeingencrypted = ''
		if totalprogress == None:
			totalprogress = ''

		return "{0}\t{1}".format(self.filebeingencrypted, self.totalprogress)

	def lastItemInStatusLog(self):
		return self.lastLogEntry

	def shortTotalProgress(self):
		totalprogress = self.totalprogress
		if totalprogress == None:
			totalprogress = 0
		return "{}".format(totalprogress)	

	def progressInfo(self):
		return json.dumps({'totalProgress':self.shortTotalProgress(), 'lastLogItem':self.lastItemInStatusLog()}) 	

if __name__ == '__main__':
	print 'test'


	




