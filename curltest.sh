
curl --request POST http://172.23.103.4:5000/DecryptAsset --data-urlencode "sourceFilePath=F:\Avid_DNxHD_Test_Movie-enc.mov" --data-urlencode "destinationFilePath=F:\Avid_DNxHD_Test_Movie.mov" | python -mjson.tool
curl --request POST http://172.23.103.4:5000/EncryptAsset --data-urlencode "sourceFilePath=F:\Avid_DNxHD_Test_Movie.mov" --data-urlencode "destinationFolderPath=F:\temp" | python -mjson.tool


curl --request POST http://172.23.103.4:5000/DecryptAsset --data-urlencode "sourceFilePath=F:\Canon Video Files\Examine2\R7AB-Apple ProRes 23.98 1080p 4096 H264-enc.mov" --data-urlencode "destinationFilePath=F:\Canon Video Files\Examine2\temp\R7AB-Apple ProRes 23.98 1080p 4096 H264.mov" | python -mjson.tool
curl --request POST http://172.23.103.4:5000/EnryptAsset --data-urlencode "sourceFilePath=F:\Canon Video Files\Examine2\R7AB-Apple ProRes 23.98 1080p 4096 H264-enc.mov" --data-urlencode "destinationFilePath=F:\Canon Video Files\Examine2\temp\R7AB-Apple ProRes 23.98 1080p 4096 H264.mov" | python -mjson.tool
curl --request POST http://172.23.103.4:5000/DecryptAsset --data-urlencode "sourceFilePath=F:\Canon Video Files\Examine2\R7AB-Apple ProRes 23.98 1080p 8192 H264-enc.mov" --data-urlencode "destinationFilePath=F:\Canon Video Files\Examine2\temp\R7AB-Apple ProRes 23.98 1080p 8192 H264.mov" | python -mjson.tool
curl --request POST http://172.23.103.4:5000/DecryptAsset --data-urlencode "sourceFilePath=F:\Canon Video Files\Examine2\R7AB-Apple ProRes 23.98 1080p 16384 H264-enc.mov" --data-urlencode "destinationFilePath=F:\Canon Video Files\Examine2\temp\R7AB-Apple ProRes 23.98 1080p 16384 H264.mov" | python -mjson.tool
curl --request POST http://172.23.103.4:5000/DecryptAsset --data-urlencode "sourceFilePath=F:\Canon Video Files\Examine2\R7AB-Apple ProRes 23.98 1080p 32768 H264-enc.mov" --data-urlencode "destinationFilePath=F:\Canon Video Files\Examine2\temp\R7AB-Apple ProRes 23.98 1080p 32768 H264.mov" | python -mjson.tool