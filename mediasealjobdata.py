import os
import sys
from xml.dom.minidom import Document
from xml.dom.minidom import Node
from xml.dom.minidom import Element

def xmlArgsFromCommandLineArgs(args):
	'''
	return [self.encryptorApplicationPath, '-o', self.jobStatusOuputPath, '-templateid', self.templateID, 
	'-templatejobname', self.templateJobName, '-outputpath', destinationFolder, '-u', self.username, 
	'-p', self.password, inputAsset]
	'''
	applicationPath = args[0]
	jobStatusOuputPath = args[2]
	username = args[10]
	password = args[12]
	sourceFiles = args[13:]
	path = MediaSealXMLJobData(args[6], args[8], sourceFiles, False, args[4]).fileWithPath()

	return [applicationPath, '-o', jobStatusOuputPath, '-c', path, '-u', username, '-p', password]

class MediaSealXMLJobData(object):
	"""
	A class which defines a basic job represented with XML
	"""
	def __init__(self, title, destination, files, isFolderSource, templateID):
		self.title 			= title
		self.destination 	= destination
		self.isFolderSource = isFolderSource
		if self.isFolderSource == True:
			self.files = files
		else:
			self.files = files
		self.templateID 	= templateID

	def __str__(self):
		return self.stringRepresentation()
	
	def fileWithPath(self, path = None):
		if path is None:
			path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jobtemplate.xml")
		self.writeXMLStringToPath(path)
		return path

	def writeXMLStringToPath(self, path):
		try:
			with open(path, "w+") as f: 
				f.write(self.stringRepresentation())
		except:
			print "Error writing file"	

	def stringRepresentation(self):
		return self.baseXMLDocument().toxml(encoding="utf-8")

	def baseXMLDocument(self):
		# EncryptionJob
		# 	CreateJobData
		# 	JobName
		# 	OutputDirectoryPath
		# 	SourceFilePathList
		# 		listitem
		# 	TemplateId

		doc = Document()
		encryptionJobElement = doc.createElement('EncryptionJob')
		doc.appendChild(encryptionJobElement)

		createJobDataElement = doc.createElement('CreateJobData')
		encryptionJobElement.appendChild(createJobDataElement)

		jobNameElement = doc.createElement('JobName')
		jobNameElement.appendChild(doc.createTextNode(self.title))
		createJobDataElement.appendChild(jobNameElement)

		outputDirectoryPathElement = doc.createElement('OutputDirectoryPath')
		outputDirectoryPathElement.appendChild(doc.createTextNode(self.destination))
		createJobDataElement.appendChild(outputDirectoryPathElement)

		sourceFilePathListElement = doc.createElement('SourceFilePathList')
		createJobDataElement.appendChild(sourceFilePathListElement)

		numberOfFiles = len(self.files)
		if numberOfFiles is None or numberOfFiles == 0:
			#raise Exception('You must specify a file or folder for encryption')
			#I prefer to see how the encryptor is behaving so I will pass an empty string
			self.files = ['']
			numberOfFiles = 1


		if numberOfFiles > 1:		
			for filePath in self.files:
				filePathElement = doc.createElement('listitem')
				filePathElement.appendChild(doc.createTextNode(filePath))
				sourceFilePathListElement.appendChild(filePathElement)
		else:
			sourceFilePathListElement.appendChild(doc.createTextNode(self.files[0]))

		templateidElement = doc.createElement('TemplateId')
		templateidElement.appendChild(doc.createTextNode(self.templateID))
		createJobDataElement.appendChild(templateidElement)
		return doc	

def main():
	print MediaSealXMLJobData('Job Title', 'F:\\', ['F:\\SourceFile'], False, '1000').fileWithPath('F:\\jobdata.xml')

if __name__ == '__main__':
	main()