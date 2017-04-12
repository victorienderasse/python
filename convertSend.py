import os
import argparse
import time
from socketIO_client import SocketIO

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True, help="Camera Name")
ap.add_argument("-i", "--id", required=True, help="camera ID")
args = vars(ap.parse_args())
name = args["name"]
id = args["id"]

hote = '192.168.1.50'
port = 3000

socket = SocketIO(hote,port)

timestr = time.strftime("%d-%m-%Y_%H-%M")

print 'convert video'
os.system('MP4Box -add /home/pi/TFE/replays/'+name+'_liveRecording.h264 /home/pi/TFE/replays/'+name+'_liveRecording_'+timestr+'.mp4')
os.system("rm /home/pi/TFE/replays/"+name+"_liveRecording.h264")
print 'convert done'

print 'transfert to server'
os.system("scp /home/pi/TFE/replays/"+name+"_liveRecording_"+timestr+".mp4 victorien@"+hote+":/home/victorien/TFE/source/server/public/cameras/camera"+id+"/videos/")
os.system("rm /home/pi/TFE/replays/"+name+"_liveRecording_"+timestr+".mp4")
print 'transfert done'

socket.emit('getLiveRecordingDone',id)
