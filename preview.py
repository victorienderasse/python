from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO
import argparse
import time
import os

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", required=True, help="CameraID")
ap.add_argument("-res", "--resolution", required=True, help="Camera resolution")
ap.add_argument("-b","--brightness", required=True, help="Brightness of the camera")
ap.add_argument("-c","--contrast", required=True, help="contrast of the camera")

args = vars(ap.parse_args())

hote = "192.168.1.50"
port = 3000

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

os.system("scp /home/pi/TFE/img/preview.jpg victorien@"+hote+":/home/victorien/TFE/source/server/public/cameras/camera"+args['id']+"/live/")
os.system("rm /home/pi/TFE/img/preview.jpg")

socket.emit('previewSend', args["id"])
