from flask import Flask
from flask import request
from flask import Response

import os
import json

from datastore import WSJob
from encryptorstate import EncryptorStatus
from decryptorstate import DecryptorStatus

import startuproutines

app = Flask(__name__)

def jsonHTTPCode200WithData(data):
	return Response(response=data, status=200, mimetype="application/json")

def jsonHTTPCode202WithData(data):
	return Response(response=data, status=202, mimetype="application/json")

def jsonHTTPError400WithData(data):
	return Response(response=data, status=400, mimetype="application/json")

def jsonHTTPError409WithData(data):
	return Response(response=data, status=409, mimetype="application/json")

def jsonHTTPError503WithData(data):
	return Response(response=data, status=503, mimetype="application/json")

def actionURLSForUUID(uuid):
	urls = []
	urls.extend(statusURLSForUUID(uuid))
	urls.extend(cancelURLSForUUID(uuid))
	return urls

def statusURLSForUUID(uuid):
	statusURLRest = '/jobStatus/%s' % (uuid)
	statusURLHttp = '/jobStatus?UUID=%s' % (uuid)
	return [statusURLRest, statusURLHttp]

def cancelURLSForUUID(uuid):
	cancelURLRest = '/cancelJob/%s' % (uuid)
	cancelURLHttp = '/cancelJob?UUID=%s' % (uuid)
	return [cancelURLRest, cancelURLHttp]

@app.route('/EncryptorStatus', methods=['GET'])
def encryptorStatus():
	if EncryptorStatus().isEncryptorRunningAJob(): 
		currentUUID = EncryptorStatus().currentUUID()
		timeRemaining = WSJob(uuid=currentUUID).timeRemaining()
		return jsonHTTPCode200WithData(json.dumps({'status':'ok', 'info': 'Encryptor is in use for the next {} seconds.'.format(timeRemaining), 'currentUUID':currentUUID}))
	
	if EncryptorStatus().isEncryptorTaskRunning() == True:
		return jsonHTTPError503WithData(json.dumps({'status':'Unable to process request.', 'info': 'Encryptor is in use, but not by web service.'}))

	return jsonHTTPCode200WithData(json.dumps({'status':'ok', 'info': 'Available.'}))

@app.route('/DecryptorStatus', methods=['GET'])
def decryptorStatus():
	try:
		if DecryptorStatus().isDecryptorRunningAJob(): 
			currentUUIDs = DecryptorStatus().currentUUIDs()

			results = []
			if len(currentUUIDs) > 0:
				for uuid in currentUUIDs:
					data = json.loads(WSJob(uuid=uuid).jsonStatus())
					data['links'] = actionURLSForUUID(uuid)
					results.append(data)

				infomessage = "{} slots available.".format(DecryptorStatus().slotsAvailable())
				return jsonHTTPCode200WithData(json.dumps({'status':'ok', 'info': infomessage, 'files': results}))
			else:
				return jsonHTTPCode200WithData(json.dumps({'status':'ok', 'info': 'Available', 'files': []}))
	except Exception as e:
		print e.message
	
	return jsonHTTPCode200WithData(json.dumps({'status':'ok', 'info': 'Available.'}))

#JOB STATUS
@app.route('/jobStatus/<UUID>', methods=['GET'])
def jobStatusREST(UUID):
	return jobstatus(UUID)

@app.route('/jobStatus', methods=['GET', 'POST'])
def jobStatusHTTP():
	uuid = ''
	if request.method == 'POST':
		uuid = request.form['UUID']
	elif request.method == 'GET':
		uuid = request.args.get('UUID')

	return jobstatus(uuid)

def jobstatus(uuid):
	preexistingJob = WSJob(uuid=uuid)

	if preexistingJob.jobNotFound() == True:
		errors = ["No job with UUID {} exists".format(uuid)]
		return jsonHTTPError400WithData(json.dumps({'status':'ok', 'info': 'Unable to process request.','errors':errors}))

	data = json.loads(preexistingJob.jsonStatus())
	data['links'] = [statusURLSForUUID(uuid)]

	if preexistingJob.operationStatus < WSJob.OperationComplete():
		if preexistingJob.wasJobCancelled() == False:
			data['links'] = [actionURLSForUUID(uuid)]
		return jsonHTTPCode200WithData(json.dumps(data))
	else:
		return jsonHTTPCode200WithData(json.dumps(data))

#DECRYPT ASSET

@app.route('/DecryptAsset', methods=['POST',])
def decryptAsset():

	if DecryptorStatus().slotsAvailable() <= 0:
		currentUUIDs = DecryptorStatus().currentUUIDs()
		
		minTime = 1000
		minUUID = ''
		
		for uuid in currentUUIDs:
			uuidTime = float(WSJob(uuid=uuid).timeRemaining())
			if uuidTime < minTime:
				minTime = uuidTime
				minUUID = uuid
		
		timeRemaining = minTime
		currentUUID = uuid

		files = []
		for uuid in currentUUIDs:
			data = json.loads(WSJob(uuid=uuid).jsonStatus())
			data['links'] = actionURLSForUUID(uuid)
			files.append(data)

		infomessage ='The Decryptor Queue is full and the next slot will be available for use in the next {} seconds.'.format(timeRemaining)
		return jsonHTTPError409WithData(json.dumps({'status':'Unable to process request.', 'info': infomessage, 'timeRemaining':'{}'.format(timeRemaining), 'currentUUIDs':currentUUIDs, 'files':files}))

	#is the request properly formatted?
	errors = []
	for attr in ['sourceFilePath', 'destinationFilePath']:
		if attr not in request.form:
			errorString = 'Error: Key value pair for %s is missing.' % (attr)
			errors.append(errorString)

	if request.method == 'POST':
		if not os.path.exists(request.form['sourceFilePath']):
			errors = ["Decryptor Service can't start as the source path doesn\'t exist!"]
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors}))

		folderForDestinationFile = os.path.dirname(request.form['destinationFilePath'])
		if not os.path.exists(folderForDestinationFile):
			errors = ["Decryptor Service can't start as the destination path doesn't exist!"]
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors}))

		sourceFilePath = request.form['sourceFilePath']
		destinationFilePath = request.form['destinationFilePath']

		if WSJob.isSourceAndDestinationFileAlreadyInUse(DecryptorStatus().currentUUIDs(), sourceFilePath, destinationFilePath) == True:
			errors = ['The source file and destination file are already in use.']
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.','errors':errors}))
		
		newJob = WSJob(sourceFilePath, destinationFilePath, operationType=WSJob.Decrypt())
		DecryptorStatus().startDecryptingAsset(newJob.uuid)

		return jsonHTTPCode202WithData(json.dumps({'status':'OK', 'uuid': newJob.uuid,'links':actionURLSForUUID(newJob.uuid)}))

#ENCRYPT ASSET

@app.route('/EncryptAsset', methods=['POST',])
def encryptAsset():

	#is encryptor running and I own it then return 409
	#else return 503 information that the Encryptor is in use outside of the service
	if EncryptorStatus().isEncryptorRunningAJob(): 
		currentUUID = EncryptorStatus().currentUUID()
		timeRemaining = WSJob(uuid=currentUUID).timeRemaining()
		return jsonHTTPError409WithData(json.dumps({'status':'Unable to process request.', 'info': 'Encryptor is in use for the next {} seconds.'.format(timeRemaining), 'timeRemaining':'{}'.format(timeRemaining), 'currentUUID':currentUUID, 'links':actionURLSForUUID(currentUUID)}))
	
	if EncryptorStatus().isEncryptorTaskRunning() == True:
		return jsonHTTPError503WithData(json.dumps({'status':'Unable to process request.', 'info': 'Encryptor is in use, but not by web service.'}))

	#is the request properly formatted?
	errors = []
	for attr in ['sourceFilePath', 'destinationFolderPath']:
		if attr not in request.form:
			errorString = 'Error: Key value pair for %s is missing.' % (attr)
			errors.append(errorString)
		
	if len(errors) > 0:
		return jsonHTTPError400WithData(json.dumps({'errors':errors}))

	if request.method == 'POST':
		if not os.path.exists(request.form['sourceFilePath']):
			errors = ["Encryptor Service can't start as the source path doesn\'t exist!"]
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors}))

		if not os.path.exists(request.form['destinationFolderPath']):
			errors = ["Encryptor Service can't start as the destination path doesn't exist!"]
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors}))

		sourceFilePath = request.form['sourceFilePath']
		destinationFolderPath = request.form['destinationFolderPath']
		
		newJob = WSJob(sourceFilePath, destinationFolderPath)
		EncryptorStatus().startEncryptingAsset(newJob.uuid)

		return jsonHTTPCode202WithData(json.dumps({'status':'OK', 'uuid': newJob.uuid,'links':actionURLSForUUID(newJob.uuid)}))

@app.route('/cancelJob', methods=['GET', 'POST'])
def cancelHTTP():
	uuid = ''
	if request.method == 'POST':
		uuid = request.form['UUID']
	elif request.method == 'GET':
		uuid = request.args.get('UUID')

	return cancelOperation(uuid)

@app.route('/cancelJob/<UUID>', methods=['GET'])
def cancelREST(UUID):
	return cancelOperation(UUID)

def cancelOperation(uuid):
	
	# try:
	preexistingJob = WSJob(uuid=uuid)

	if preexistingJob.jobNotFound() == True:
		errors = ["No job with UUID {} exists.".format(uuid)]
		return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors, 'links':["/DecryptorStatus"]}))

	if preexistingJob.operationType == WSJob.Decrypt():
		currentUUIDs = DecryptorStatus().currentUUIDs()
		if uuid not in currentUUIDs:
			errors = ["The Job with UUID {} is not running. Please check the job number passed in the request.".format(uuid)]
			return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors, 'links':["/DecryptorStatus"]}))

		DecryptorStatus().stop(uuid)
		return jsonHTTPCode202WithData(json.dumps({'status':'OK', 'links':statusURLSForUUID(uuid)}))

	else:
		if EncryptorStatus().isEncryptorRunningAJob() == True:
			if EncryptorStatus().currentUUID() != uuid:
				errors = ["The Job with UUID {} is not running. Please check the job number passed in the request.".format(uuid)]
				return jsonHTTPError400WithData(json.dumps({'status':'Unable to process request.', 'errors':errors, 'links':["/EncryptorStatus"]}))
			else:
				EncryptorStatus().stop(uuid)
				return jsonHTTPCode202WithData(json.dumps({'status':'OK', 'links':statusURLSForUUID(uuid)}))

		if EncryptorStatus().isEncryptorTaskRunning() == True:
			errors = ["The Job with UUID {} is not running.".format(uuid)]
			errors.append("It appears that the Encryptor is not accessible.")
			return jsonHTTPError503WithData(json.dumps({'status':'Unable to process request.', 'errors':errors}))
	
	# except Exception as e:
	# 	print e.message

if __name__ == '__main__':
	startuproutines.initialize()
	app.run(host='0.0.0.0', port=5000)
