from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import imutils
import json
import time
import cv2
import os
from socketIO_client import SocketIO

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
ap.add_argument("-n", "--name", required=True, help="Name of the camera")
ap.add_argument("-i", "--id", required=True, help="ID of the camera")
ap.add_argument("-t", "--time", required=True, help="Time to process")
ap.add_argument("-o", "--once", required=False, help="exec just once")
ap.add_argument("-p", "--planningID", required=False, help="planningID")
args = vars(ap.parse_args())
name = args["name"]
id = args["id"]
once = args["once"]
planningID = args["planningID"]
timeProcess = args["time"]
timeProcess = int(timeProcess)

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]
user = conf["user"]

#tell the server the motion detection start
socket = SocketIO(hote,port)
if timeProcess > 0:
	socket.emit('motionDetectionStart', id)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (conf["width"],conf["height"])
camera.framerate = conf["fps"]
camera.brightness = conf["brightness"]
camera.contrast = conf["contrast"]
rawCapture = PiRGBArray(camera, size=(conf["width"],conf["height"]))

# allow the camera to warmup, then initialize the average frame, and frame motion counter
print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
avg = None
motionCounter = 0
if timeProcess > 0:
	timeProcess1 = time.time()

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array
	state = "Unoccupied"

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the average frame is None, initialize it
	if avg is None:
		print "[INFO] starting background model..."
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < conf["min_area"]:
			continue

		# update the state
		state = "Occupied"

	# check to see if the room is occupied
	if state == "Occupied":
		print "occupied"
		#Send sms
		#message = "Warning ! Something has been detected by camera "+name
		#message = client.messages.create(to='+32474227310',from_='+32460207648',body=message)
		#Get Datetime
		timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
		fileName = name+'_motionDetection_'+timestr
		socket.emit('motionDetected', {'cameraID': id, 'timestr': timestr})
		#Start recording
		camera.start_recording("/home/pi/TFE/replays/"+fileName+".h264")
		print("Recording..")
		camera.wait_recording(conf["time_record"])
		camera.stop_recording()
		print("Stop recording")	
		#Convert video to mp4 because of damn Chrome
		print("convert video")
		os.system("MP4Box -add /home/pi/TFE/replays/"+fileName+".h264 /home/pi/TFE/replays/"+fileName+".mp4")
		os.system("rm /home/pi/TFE/replays/"+fileName+".h264")
		#transfer to server
		print("Transfer to server")
		os.system("scp /home/pi/TFE/replays/"+fileName+".mp4 "+user+"@"+hote+":/home/"+user+"/TFE/source/server/public/cameras/camera"+id+"/videos/")
		os.system("rm /home/pi/TFE/replays/"+fileName+".mp4")
		
		socket.emit('motionDetectedSend', {'cameraID': id, 'fileName': fileName+'.mp4', 'type':'det'})
		
	# otherwise, the room is not occupied
	else:		
		motionCounter = 0

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)	

	if timeProcess > 0:
		timeProcess2 = time.time()
		timeProcess3 = timeProcess2-timeProcess1
		print 'timeProcess3 : ',timeProcess3
		if timeProcess3 > timeProcess:
			print 'break'
			socket.emit('motionDetectionStop', {'cameraID': id, 'once': once, 'planningID': planningID})
			break;
