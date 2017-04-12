from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO
import argparse
import warnings
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", required=True, help="ID of the camera")
ap.add_argument("-r", "--record", required=True, help="record or not record")
ap.add_argument("-n", "--name", required=True, help="Camera name")
args = vars(ap.parse_args())
cameraID = args["id"]
record = args["record"]
if(record == 'False'):
	record = False
else:
	record = True
name = args["name"]

print 'name : '+name

hote = "192.168.1.50"
port = 3000

socket = SocketIO(hote,port)

camera = PiCamera()
camera.resolution = (640,480)

print record
if (record):
	print 'recording'
	camera.start_recording('/home/pi/TFE/replays/'+name+'_liveRecording.h264')

print('start stream to camera'+cameraID)

while True:
	if (record):
		print 'capture recording'
		camera.wait_recording(0.5)
		camera.capture('/home/pi/TFE/img/stream_camera_'+cameraID+'.jpg', use_video_port=True)
	else:
		print 'capture picture'
		camera.capture('/home/pi/TFE/img/stream_camera_'+cameraID+'.jpg')
		print 'end capture picture'
	print 'sending img'
	os.system('scp /home/pi/TFE/img/stream_camera_'+cameraID+'.jpg victorien@'+hote+':/home/victorien/TFE/source/server/public/cameras/camera'+cameraID+'/live/')
	print('send')
	socket.emit('streamSend', cameraID)

