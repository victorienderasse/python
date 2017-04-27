import json
import os
import argparse
import time
from socketIO_client import SocketIO
import warnings

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True, help="Camera Name")
ap.add_argument("-i", "--id", required=True, help="camera ID")
ap.add_argument("-c", "--conf", required=True, help="conf file")
args = vars(ap.parse_args())
name = args["name"]
id = args["id"]

warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]
user = conf["user"]

socket = SocketIO(hote,port)

timestr = time.strftime("%d-%m-%Y_%H-%M")

print 'convert video'
os.system('MP4Box -add /home/pi/TFE/replays/'+name+'_liveRecording.h264 /home/pi/TFE/replays/'+name+'_liveRecording_'+timestr+'.mp4')
os.system("rm /home/pi/TFE/replays/"+name+"_liveRecording.h264")
print 'convert done'

print 'transfert to server'
os.system("scp /home/pi/TFE/replays/"+name+"_liveRecording_"+timestr+".mp4 "+user+"@"+hote+":/home/"+user+"/TFE/source/server/public/cameras/camera"+id+"/videos/")
os.system("rm /home/pi/TFE/replays/"+name+"_liveRecording_"+timestr+".mp4")
print 'transfert done'

socket.emit('getLiveRecordingDone',id)
