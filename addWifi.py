import io
import zbar
import json
import time
from socketIO_client import SocketIO
from PIL import Image
import picamera
import os
import argparse
import warnings

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", required=True, help="CameraID")
ap.add_argument("-c", "--conf", required=True, help="conf file")
args = vars(ap.parse_args())
cameraID = args["id"]

warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

hote = conf["hote"]
port = conf["port"]

socket = SocketIO(hote,port)

def QRScan():
	i=0
	print 'start scanning'
	data = ''
        camera = picamera.PiCamera()
        time.sleep(1)
        #camera.start_preview()

        #Create and configure the reader
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')

	#Create and configure the reader
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')

        while(data == '' and i < 500):

                #Create the in-memory stream
                stream = io.BytesIO()
                camera.capture(stream, format="jpeg")

                #"Rewind" the stream to the beginning so we can read its content
                stream.seek(0)

                pil = Image.open(stream)
                pil = pil.convert('L')
                width, height = pil.size
                raw = pil.tobytes()

                #wrap image data
                image = zbar.Image(width, height, 'Y800', raw)

                #Scan the image
                scanner.scan(image)

                #extract the result
                for symbol in image:
                        data = symbol.data
                        return data
                        camera.close()

                #clean up
                del(image)
                i = i + 1



scan = QRScan()
mot = 0
userID = ''
ssid = ''
password = ''

for lettre in scan:
	if lettre in ' ':
		print 'nouveau mot'
		mot = mot + 1
	else:
		if(mot == 0):
			userID = userID + lettre
		else:
			if(mot == 1):
				ssid = ssid + lettre
			else:
				password = password + lettre


addWifi = '''network={
	ssid="''' + ssid + '''"
	psk="''' + password + '''"
	key_mgmt=WPA-PSK
}'''

cmd = 'sudo echo \'' + addWifi + '\' >> /etc/wpa_supplicant/wpa_supplicant.conf'
os.system(cmd)


#p = os.popen('cat /proc/cpuinfo | grep Serial | cut -d ":" -f 2')
#serial = p.readline()

socket.emit('addWifiDone',{'userID':userID,'cameraID':cameraID})
