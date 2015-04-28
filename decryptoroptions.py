import os
import json

class DecryptorOptions():
	def __init__(self):
		configurationOptions = self.configurationOptions()
		self.decryptorApplicationPath = configurationOptions['decryptorApplicationPath']
		self.decryptorSlots = int(configurationOptions['decryptorSlots'])

	def allKeys(self):
		return ['decryptorApplicationPath', 'decryptorSlots']

	def pathKeys(self):
		return ['decryptorApplicationPath']

	def folderKeys(self):
		return []

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

	def decryptorOptionsWithInputAssetAndDestinationFile(self, inputAsset, destinationFile):
		return [self.decryptorApplicationPath, inputAsset, destinationFile]

if __name__ == '__main__':
	print DecryptorOptions().decryptorSlots, type(DecryptorOptions().decryptorSlots)