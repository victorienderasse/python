from picamera.array import PiRGBArray
from picamera import PiCamera
from socketIO_client import SocketIO
import argparse
import warnings
import time
import json
import os

#construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="Path to the JSON configuration file")
ap.add_argument("-t", "--time", required=True, help="time to record")
ap.add_argument("-n", "--name", required=True, help="Name of the camera recording")
ap.add_argument("-i", "--id", required=True, help="CameraID")
ap.add_argument("-o", "--once", required=False, help="exec just once")
ap.add_argument("-p", "--planningID", required=False, help="planningID")
args = vars(ap.parse_args())
time_record = int(args["time"])
name = args["name"]
id = args["id"]
once = args["once"]
planningID = args["planningID"]

#filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]
user = conf["user"]

socket = SocketIO(hote,port)
socket.emit('recordStart',id)

#Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (conf["width"],conf["height"])
camera.framerate = conf["fps"]
camera.brightness = conf["brightness"]
camera.contrast = conf["contrast"]

#rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

#Warmup the camera
print("[INFO] Warming up..")
time.sleep(conf["camera_warmup_time"])

#get date time
timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
fileName = name+'_record_'+timestr 

#Start recording
print("recording..")
camera.start_recording("/home/pi/TFE/replays/"+fileName+".h264")
camera.wait_recording(time_record)
camera.stop_recording()
print("end Recording")

#convert video to mp4 format because of damn Chrome
print("convert video")
os.system("MP4Box -add /home/pi/TFE/replays/"+fileName+".h264 /home/pi/TFE/replays/"+fileName+".mp4")
os.system("rm /home/pi/TFE/replays/"+fileName+".h264")
print("convert done")

#trasfert video to server
print("trasfer to server")
os.system("scp /home/pi/TFE/replays/"+fileName+".mp4 "+user+"@"+hote+":/home/"+user+"/TFE/source/server/public/cameras/camera"+id+"/videos/")
os.system("rm /home/pi/TFE/replays/"+fileName+".mp4")

socket.emit('recordStop',{'cameraID': id, 'once': once, 'planningID': planningID, 'fileName': fileName+'.mp4', 'type': 'rec'})

camera.close()
