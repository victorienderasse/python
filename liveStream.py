from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO
import argparse
import warnings
import json
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf",required=True, help="config file")
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

warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]
user = conf["user"]

print 'server : '+hote+':'+str(port)

socket = SocketIO(hote,port)

camera = PiCamera()
camera.resolution = (conf["width"],conf["height"])
camera.framerate = conf["fps"]
camera.brightness = conf["brightness"]
camera.contrast = conf["contrast"]

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
	os.system('scp /home/pi/TFE/img/stream_camera_'+cameraID+'.jpg '+user+'@'+hote+':/home/victorien/TFE/source/server/public/cameras/camera'+cameraID+'/live/')
	print('send')
	socket.emit('streamSend', cameraID)

