import json
from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO
import argparse
import time
import os
import warnings

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", required=True, help="CameraID")
ap.add_argument("-res", "--resolution", required=True, help="Camera resolution")
ap.add_argument("-b","--brightness", required=True, help="Brightness of the camera")
ap.add_argument("-ct","--contrast", required=True, help="contrast of the camera")
ap.add_argument("-c","--conf",required=True,help="conf file")
args = vars(ap.parse_args())

warnings.filterwarnings
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]
user = conf["user"]

socket = SocketIO(hote,port)

camera = PiCamera()
if(int(args["resolution"]) == 1):
	camera.resolution = (640,480)
else:
	if(int(args["resolution"]) == 2):
		camera.resolution = (1200,900)
	else:
		camera.resolution = (1600,1200)

camera.brightness = int(args["brightness"])
camera.contrast = int(args["contrast"])

camera.capture("/home/pi/TFE/img/preview.jpg")

camera.close()

os.system("scp /home/pi/TFE/img/preview.jpg "+user+"@"+hote+":/home/"+user+"/TFE/source/server/public/cameras/camera"+args['id']+"/live/")
os.system("rm /home/pi/TFE/img/preview.jpg")

socket.emit('previewSend', args["id"])
